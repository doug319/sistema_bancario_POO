import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime 

class Cliente:
    def __init__(self,endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self,conta,transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self,conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self,numero,cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls,cliente,numero):
        return cls(numero,cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self,valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não possui saldo suficiente. @@@")
        elif valor > 0:
            self._saldo -= valor
            print("\n Saque Realizado com sucesso.")
            return True
        else:
            print("\n Operação falhou. Valor informado é inválido.")
        
        return False
    
    def depositar(self,valor):
        if valor > 0:
            self._saldo += valor
            print("\n Depósito Realizado com sucesso.")
        else:
            print("\n Operação falhou. Valor informado é inválido.")
            return False
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
    
    def sacar(self,valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
            )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques
    
        if excedeu_limite:
            print("\n@@@@ Operação falhou. O valor excedeu o limite. @@@")
        elif excedeu_saques:
            print("\n@@@@ Operação falhou. O valor excedeu de saques. @@@")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
    
class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self,transacao):
        self._transacoes.append(
            {"tipo":transacao.__class__.__name__,"valor":transacao.valor}
            )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self,conta):
        pass

class Saque(Transacao):
    def __init__(self,valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self,conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self,valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self,conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
    =========== MENU ===========
    [d]\t Depositar
    [s]\t Sacar
    [e]\t Extrato
    [nc]\t Nova Conta
    [lc]\t Listar Contas
    [nu]\t Novo Usuário
    [q]\t Sair 
    => """
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf,clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta.")
        return
    
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado.")
        return
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta,transacao)

def sacar(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado.")
        return
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta,transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado.")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n===========EXTRATO===========")
    transacoes = conta.historico.transacoes
    extrato = ""
    if  not transacoes:
        extrato = "Não foram realizadas movimentações"
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"
    
    print(extrato)
    print(f"\n Saldo:\n\tR$ {conta.saldo:.2f}")
    print("============================")

def criar_cliente(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if cliente:
        print("\n@@@ JCPF já cadastrado.")
        return
    
    nome = input("Informe seu nome completo: ")
    data_nascimento = input("Informe sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe seu endereço (logradouro, numero - bairro - cidade/UF): ")

    cliente = PessoaFisica(cpf = cpf, nome = nome, data_nascimento = data_nascimento, endereco = endereco)
    clientes.append(cliente)

    print("Cliente cadastrado com sucesso.")

def criar_conta(numero_conta,clientes,contas):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado. Não é possivel criar conta.")
        return
    
    conta = ContaCorrente.nova_conta(cliente = cliente, numero = numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    
    print("\n Nova Conta Criada com Sucesso.")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        if opcao == "s":
            sacar(clientes)
        if opcao == "e":
            exibir_extrato(clientes)
        if opcao == "nu":
            criar_cliente(clientes)
        if opcao == "nc":
            numero_conta = len(contas)+1
            criar_conta(numero_conta,clientes,contas)
        if opcao == "lc":
            listar_contas(contas)
        if opcao == "q":
            break

main()