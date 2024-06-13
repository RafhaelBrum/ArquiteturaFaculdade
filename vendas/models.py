from django.db import models

class Fabricante(models.Model):
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    endereco = models.TextField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField()
    vendedor = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_fantasia

class Grupo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class SubGrupo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    quantidade_comprado = models.IntegerField()
    quantidade_vendido = models.IntegerField(default=0)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    subgrupo = models.ForeignKey(SubGrupo, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto.nome} - {self.data_hora}"
