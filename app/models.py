from django.db import models

class NotaFiscal(models.Model):
    controle = models.CharField(max_length=50, unique=True)
    nome_cliente = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    transp = models.CharField(max_length=100)
    vol = models.IntegerField()
    obs = models.TextField(blank=True)
    chave_nfe = models.CharField(max_length=44)
    emissao = models.DateField()

    class Meta:
        db_table = 'notas_fiscais'  # nome exato da tabela no banco
        managed = False  # Django não cria/alterar essa tabela

    def __str__(self):
        return f'{self.controle} - {self.nome_cliente}'