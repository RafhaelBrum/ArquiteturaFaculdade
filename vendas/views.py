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

class VendaCreateView(LoginRequiredMixin, CreateView):
    model = Venda
    fields = ['produto', 'quantidade']
    template_name = 'vendas/venda_form.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.vendedor = self.request.user
        return super().form_valid(form)

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