from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .models import Produto, Fabricante, Grupo, SubGrupo, Venda
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import UserRegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count
import plotly.graph_objs as go
import plotly.express as px
from django.db.models.functions import ExtractMonth
from django.utils.timezone import now
from datetime import datetime, timedelta

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()

class ProdutoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Produto
    fields = ['nome', 'descricao', 'preco_custo', 'preco_venda', 'peso', 'quantidade_comprado', 'fabricante', 'grupo', 'subgrupo']
    template_name = 'vendas/produto_form.html'
    success_url = reverse_lazy('index')

class FabricanteCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Fabricante
    fields = ['nome_fantasia', 'razao_social', 'cnpj', 'endereco', 'telefone', 'email', 'vendedor']
    template_name = 'vendas/fabricante_form.html'
    success_url = reverse_lazy('index')

class GrupoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Grupo
    fields = ['nome', 'descricao']
    template_name = 'vendas/grupo_form.html'
    success_url = reverse_lazy('index')

class SubGrupoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = SubGrupo
    fields = ['nome', 'descricao', 'grupo']
    template_name = 'vendas/subgrupo_form.html'
    success_url = reverse_lazy('index')

class VendaCreateView(CreateView):
    model = Venda
    fields = ['produto', 'quantidade']
    template_name = 'vendas/venda_form.html'
    success_url = '/'

    def form_valid(self, form):
        produto = form.cleaned_data['produto']
        quantidade_vendida = form.cleaned_data['quantidade']

        if produto.quantidade_comprado >= quantidade_vendida:
            produto.quantidade_comprado -= quantidade_vendida
            produto.save() 
            
            form.instance.vendedor = self.request.user
            return super().form_valid(form)
        else:
            form.add_error('quantidade', 'Não há estoque suficiente para realizar esta venda.')

            return self.form_invalid(form)
        
def index(request):
    return render(request, 'vendas/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'admin':
                group = Group.objects.get(name='Admin')
            else:
                group = Group.objects.get(name='Funcionário')
            user.groups.add(group)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'vendas/register.html', {'form': form})

def lista_produtos(request):
    grupos = Grupo.objects.all()
    subgrupos = SubGrupo.objects.all()
    produtos = Produto.objects.all()

    context = {
        'grupos': grupos,
        'subgrupos': subgrupos,
        'produtos': produtos,
    }

    return render(request, 'vendas/lista_produtos.html', context)

def visualizar_vendas(request):
    
    # Gráfico de Linha: Vendas mensais (custo total e venda total)
    vendas_mensais = Venda.objects.annotate(mes=ExtractMonth('data_hora')).filter(data_hora__year=now().year).values('mes').annotate(custo_total=Sum('produto__preco_custo'), venda_total=Sum('produto__preco_venda'))
    meses = [datetime.strptime(str(m['mes']), "%m").strftime("%B") for m in vendas_mensais]
    custo_total = [m['custo_total'] if m['custo_total'] else 0 for m in vendas_mensais]
    venda_total = [m['venda_total'] if m['venda_total'] else 0 for m in vendas_mensais]

    # Gráfico de Barras: Quantidade comprada e quantidade vendida mensal
    produtos_mensais = Venda.objects.annotate(mes=ExtractMonth('data_hora')).filter(data_hora__year=now().year).values('mes').annotate(quantidade_comprada=Sum('produto__quantidade_comprado'), quantidade_vendida=Sum('quantidade'))
    quantidade_comprada = [p['quantidade_comprada'] if p['quantidade_comprada'] else 0 for p in produtos_mensais]
    quantidade_vendida = [p['quantidade_vendida'] if p['quantidade_vendida'] else 0 for p in produtos_mensais]

    # Gráfico de Dispersão: Percentual de lucro dos produtos vendidos mensalmente
    lucro_percentual = []
    for mes in range(1, 13):
        vendas_mes = Venda.objects.filter(data_hora__month=mes, data_hora__year=now().year)
        total_custo = sum([venda.produto.preco_custo * venda.quantidade for venda in vendas_mes])
        total_venda = sum([venda.produto.preco_venda * venda.quantidade for venda in vendas_mes])
        if total_custo > 0:
            lucro_percentual.append((total_venda - total_custo) / total_custo * 100)
        else:
            lucro_percentual.append(0)

    # Gráfico de Pizza: Os 3 produtos mais vendidos em quantidade mensal
    top_produtos = Venda.objects.values('produto__nome').annotate(quantidade_total=Sum('quantidade')).order_by('-quantidade_total')[:3]
    nomes_produtos = [p['produto__nome'] for p in top_produtos]
    quantidade_produtos = [p['quantidade_total'] for p in top_produtos]

    # Gráfico de Barras e Linha: Grupos mais vendidos com meta de >= 1000 unidades
    grupos_mais_vendidos = Grupo.objects.annotate(quantidade_total=Sum('produto__venda__quantidade')).filter(quantidade_total__gte=1000).order_by('-quantidade_total')[:4]
    nomes_grupos = [g.nome for g in grupos_mais_vendidos]
    quantidade_grupos = [g.quantidade_total for g in grupos_mais_vendidos]

    # Tabela Analítica: Produtos com estoque baixo
    produtos_estoque_baixo = Produto.objects.filter(quantidade_comprado__lt=10).order_by('-quantidade_comprado')

    # Gráfico de Linha
    grafico_linha = go.Figure()
    grafico_linha.add_trace(go.Scatter(x=meses, y=custo_total, mode='lines+markers', name='Custo Total'))
    grafico_linha.add_trace(go.Scatter(x=meses, y=venda_total, mode='lines+markers', name='Venda Total'))
    grafico_linha.update_layout(title='Vendas Mensais - Custo Total e Venda Total')

    # Gráfico de Barras
    grafico_barras = go.Figure()
    grafico_barras.add_trace(go.Bar(x=meses, y=quantidade_comprada, name='Quantidade Comprada'))
    grafico_barras.add_trace(go.Bar(x=meses, y=quantidade_vendida, name='Quantidade Vendida'))
    grafico_barras.update_layout(barmode='group', title='Quantidade Comprada e Vendida Mensalmente')

    # Gráfico de Dispersão
    grafico_dispersao = go.Figure()
    grafico_dispersao.add_trace(go.Scatter(x=list(range(1, 13)), y=lucro_percentual, mode='markers', name='Lucro Percentual'))
    grafico_dispersao.update_layout(title='Percentual de Lucro Mensal')

    # Gráfico de Pizza
    grafico_pizza = px.pie(values=quantidade_produtos, names=nomes_produtos, title='Produtos Mais Vendidos em Quantidade')

    # Gráfico de Barras e Linha
    grafico_barras_linha = go.Figure()
    grafico_barras_linha.add_trace(go.Bar(x=nomes_grupos, y=quantidade_grupos, name='Quantidade Vendida'))
    grafico_barras_linha.update_layout(title='Grupos mais Vendidos (>= 1000 unidades)')

    context = {
        'grafico_linha': grafico_linha.to_html(include_plotlyjs='cdn'),
        'grafico_barras': grafico_barras.to_html(include_plotlyjs='cdn'),
        'grafico_dispersao': grafico_dispersao.to_html(include_plotlyjs='cdn'),
        'grafico_pizza': grafico_pizza.to_html(include_plotlyjs='cdn'),
        'grafico_barras_linha': grafico_barras_linha.to_html(include_plotlyjs='cdn'),
        'produtos_estoque_baixo': produtos_estoque_baixo,
    }

    return render(request, 'vendas/visualizar_vendas.html', context)