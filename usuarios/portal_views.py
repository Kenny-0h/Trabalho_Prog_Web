from functools import wraps
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from agenda.models import Agenda, Disponibilidade, BloqueioAgenda, Especialidade, SolicitacaoDisponibilidade
from atendimento.models import Consulta, Prontuario, Exame, Receita
from .models import Usuario, Paciente, Medico

ADMIN = (Usuario.TipoUsuario.ADMINISTRADOR, Usuario.TipoUsuario.FUNCIONARIO)

def allowed(*roles):
    def deco(fn):
        @wraps(fn)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.tipo_usuario not in roles:
                messages.error(request, "Você não tem permissão para acessar esta tela.")
                return redirect("inicio")
            return fn(request, *args, **kwargs)
        return wrapped
    return deco

@login_required
def home(request):
    u=request.user
    links=[]
    if u.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
        links=[("Consultar horários disponíveis","/portal/disponibilidade/"),("Minhas consultas","/portal/minhas-consultas/")]
        perfil=getattr(u,"perfil_paciente",None)
    elif u.tipo_usuario == Usuario.TipoUsuario.MEDICO:
        links=[("Minha agenda","/portal/minha-agenda/"),("Cadastrar disponibilidade","/portal/minha-agenda/nova/"),("Solicitar bloqueio/alteração","/portal/minha-agenda/bloqueio/"),("Minhas consultas","/portal/minhas-consultas-medico/")]
        perfil=getattr(u,"perfil_medico",None)
    else:
        links=[("Consultas","/portal/consultas/"),("Pacientes","/portal/pacientes/"),("Médicos","/portal/medicos/"),("Especialidades","/portal/especialidades/"),("Agendas e disponibilidades","/portal/agendas/"),("Solicitações de bloqueio","/portal/bloqueios/")]
        if u.tipo_usuario == Usuario.TipoUsuario.ADMINISTRADOR:
            links.extend([("Prontuários","/portal/registros/prontuario/"),("Exames","/portal/registros/exame/"),("Receitas","/portal/registros/receita/")])
        perfil=getattr(u,"perfil_administrador",None) or getattr(u,"perfil_funcionario",None)
    return render(request,"portal/home.html",{"perfil":perfil,"links":links})

def _list(request, title, qs, fields, create_url=None, filters=None, can_edit=True, can_delete=True):
    q=request.GET.get("q","").strip()
    if q:
        search=Q()
        for f in filters or []: search |= Q(**{f+"__icontains":q})
        qs=qs.filter(search)
    extra=request.GET.get("filtro","")
    if extra:
        key={"Pacientes":"usuario__cpf","Médicos":"crm","Especialidades":"nome","Consultas":"status","Minhas consultas":"status","Horários disponíveis":"agenda__medico__especialidade__nome","Minha agenda":"agenda__medico__especialidade__nome","Solicitações de bloqueio":"status"}.get(title)
        if key:
            qs=qs.filter(**{key+"__icontains":extra})
    paginator=Paginator(qs, 20)
    page_obj=paginator.get_page(request.GET.get("page"))
    linhas=[]
    for obj in page_obj.object_list:
        cells=[]
        for label, path in fields.items():
            valor=obj
            for parte in path.split("__"):
                valor=getattr(valor,parte,None)
            if hasattr(valor,"strftime"): valor=valor.strftime("%d/%m/%Y %H:%M") if "horario" not in path else valor.strftime("%H:%M")
            elif path=="dia_semana" and valor is not None: valor=obj.get_dia_semana_display()
            elif path=="status" and hasattr(obj,"get_status_display"): valor=obj.get_status_display()
            cells.append(str(valor if valor is not None else "—"))
        linhas.append((obj,cells))
    slug={"Pacientes":"paciente","Médicos":"medico","Especialidades":"especialidade","Agendas":"agenda","Consultas":"consulta","Minhas consultas":"consulta","Horários disponíveis":"disponibilidade","Minha agenda":"disponibilidade","Solicitações de bloqueio":"bloqueio","Prontuários":"prontuario","Exames":"exame","Receitas":"receita"}.get(title,"consulta")
    return render(request,"portal/lista.html",{"titulo":title,"linhas":linhas,"campos":fields,"q":q,"extra":extra,"create_url":create_url,"can_edit":can_edit,"can_delete":can_delete,"slug":slug,"page_obj":page_obj})

def _crud(model, title, fields, qs, search_fields, roles=ADMIN, create=True, edit=True, delete=True, detail=True):
    class F(forms.ModelForm):
        class Meta:
            model=model
            fields=fields
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw)
            for f in self.fields.values():
                f.widget.attrs["class"]="form-select" if isinstance(f.widget,forms.Select) else "form-control"
                if isinstance(f, forms.DateTimeField): f.widget=forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-control"},format="%Y-%m-%dT%H:%M")
    return F

def _form(request, model, fields, title, back, obj=None):
    F=forms.modelform_factory(model, fields=fields, widgets={})
    form=F(request.POST or None, instance=obj)
    for f in form.fields.values():
        f.widget.attrs["class"]="form-select" if isinstance(f.widget,forms.Select) else "form-control"
        if isinstance(f,forms.DateTimeField): f.widget=forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-control"},format="%Y-%m-%dT%H:%M")
    if request.method=="POST" and form.is_valid():
        item=form.save()
        messages.success(request,"Registro salvo com sucesso.")
        return redirect(back, item.pk) if back=="portal_consulta_detalhe" else redirect(back)
    return render(request,"portal/form.html",{"form":form,"titulo":title,"voltar":reverse(back)})

@allowed(*ADMIN)
def pacientes(request):
    return _list(request,"Pacientes",Paciente.objects.select_related("usuario").order_by("usuario__nome"),{"Nome":"usuario__nome","CPF":"usuario__cpf","Plano":"plano_medico"},create_url="/gestao/pacientes/novo/",filters=["usuario__nome","usuario__cpf","plano_medico"])
@allowed(*ADMIN)
def medicos(request):
    return _list(request,"Médicos",Medico.objects.select_related("usuario","especialidade").order_by("usuario__nome"),{"Nome":"usuario__nome","CRM":"crm","Especialidade":"especialidade__nome"},create_url="/gestao/medicos/novo/",filters=["usuario__nome","crm","especialidade__nome"])
@allowed(*ADMIN)
def especialidades(request):
    return _list(request,"Especialidades",Especialidade.objects.all(),{"Nome":"nome","Duração (min)":"tempo_medio_consulta"},create_url="/admin/agenda/especialidade/add/",filters=["nome"])
@allowed(*ADMIN)
def agendas(request):
    return _list(request,"Agendas",Agenda.objects.select_related("medico__usuario").prefetch_related("disponibilidades"),{"Médico":"medico__usuario__nome"},filters=["medico__usuario__nome"])
@allowed(*ADMIN)
def consultas(request):
    qs=Consulta.objects.select_related("paciente__usuario","medico__usuario","medico__especialidade")
    return _list(request,"Consultas",qs,{"Paciente":"paciente__usuario__nome","Médico":"medico__usuario__nome","Data":"data_hora","Status":"status"},create_url="/portal/consultas/nova/",filters=["paciente__usuario__nome","medico__usuario__nome","status"])
@allowed(*ADMIN)
def consulta_nova(request):
    return _form(request,Consulta,["paciente","medico","data_hora","status"],"Nova consulta","portal_consultas")
@allowed(*ADMIN)
def consulta_editar(request,pk):
    return _form(request,Consulta,["paciente","medico","data_hora","status"],"Editar consulta","portal_consultas",get_object_or_404(Consulta,pk=pk))
@allowed(*ADMIN)
def consulta_excluir(request,pk):
    obj=get_object_or_404(Consulta,pk=pk)
    if request.method=="POST": obj.delete(); messages.success(request,"Consulta excluída."); return redirect("portal_consultas")
    return render(request,"portal/excluir.html",{"objeto":obj,"voltar":reverse("portal_consultas")})
@login_required
def consulta_detalhe(request,pk):
    c=get_object_or_404(Consulta.objects.select_related("paciente__usuario","medico__usuario","medico__especialidade"),pk=pk)
    u=request.user
    if u.tipo_usuario==Usuario.TipoUsuario.PACIENTE and c.paciente.usuario_id!=u.id: return redirect("inicio")
    if u.tipo_usuario==Usuario.TipoUsuario.MEDICO and c.medico.usuario_id!=u.id: return redirect("inicio")
    if u.tipo_usuario not in (Usuario.TipoUsuario.PACIENTE,Usuario.TipoUsuario.MEDICO,*ADMIN) or u.tipo_usuario == Usuario.TipoUsuario.FUNCIONARIO: return redirect("inicio")
    prontuario=getattr(c,"prontuario",None)
    return render(request,"portal/consulta_detalhe.html",{"consulta":c,"prontuario":prontuario,"exames":prontuario.exames.all() if prontuario else [],"receitas":prontuario.receitas.all() if prontuario else []})

@login_required
@allowed(Usuario.TipoUsuario.PACIENTE)
def minhas_consultas(request):
    qs=Consulta.objects.filter(paciente__usuario=request.user).select_related("medico__usuario","medico__especialidade")
    return _list(request,"Minhas consultas",qs,{"Médico":"medico__usuario__nome","Data":"data_hora","Status":"status"},filters=["medico__usuario__nome","status"])
@login_required
@allowed(Usuario.TipoUsuario.MEDICO)
def consultas_medico(request):
    qs=Consulta.objects.filter(medico__usuario=request.user).select_related("paciente__usuario")
    return _list(request,"Minhas consultas",qs,{"Paciente":"paciente__usuario__nome","Data":"data_hora","Status":"status"},filters=["paciente__usuario__nome","status"])
@login_required
@allowed(Usuario.TipoUsuario.PACIENTE)
def disponibilidade(request):
    qs=Disponibilidade.objects.select_related("agenda__medico__usuario","agenda__medico__especialidade")
    return _list(request,"Horários disponíveis",qs,{"Médico":"agenda__medico__usuario__nome","Especialidade":"agenda__medico__especialidade__nome","Dia":"dia_semana","Início":"horario_inicio","Fim":"horario_fim"},filters=["agenda__medico__usuario__nome","agenda__medico__especialidade__nome"])
@login_required
@allowed(Usuario.TipoUsuario.MEDICO)
def agenda_medico(request):
    qs=Disponibilidade.objects.filter(agenda__medico__usuario=request.user).select_related("agenda__medico__especialidade")
    return _list(request,"Minha agenda",qs,{"Especialidade":"agenda__medico__especialidade__nome","Dia":"dia_semana","Início":"horario_inicio","Fim":"horario_fim"},filters=["agenda__medico__especialidade__nome"])
@login_required
@allowed(Usuario.TipoUsuario.MEDICO)
def disponibilidade_nova(request):
    agenda=get_object_or_404(Agenda,medico__usuario=request.user)
    return _form(request,Disponibilidade,["dia_semana","horario_inicio","horario_fim"],"Cadastrar disponibilidade","portal_agenda_medico")
@login_required
@allowed(Usuario.TipoUsuario.MEDICO)
def disponibilidade_editar(request,pk):
    obj=get_object_or_404(Disponibilidade,pk=pk,agenda__medico__usuario=request.user)
    return _form(request,Disponibilidade,["dia_semana","horario_inicio","horario_fim"],"Editar disponibilidade","portal_agenda_medico",obj)
@login_required
@allowed(Usuario.TipoUsuario.MEDICO)
def bloqueio_novo(request):
    agenda=get_object_or_404(Agenda,medico__usuario=request.user)
    if request.method=="POST":
        F=forms.modelform_factory(BloqueioAgenda,fields=["data_hora_inicio","data_hora_fim","justificativa","tipo"])
        form=F(request.POST)
        if form.is_valid():
            b=form.save(commit=False); b.agenda=agenda; b.save(); messages.success(request,"Solicitação enviada para análise."); return redirect("portal_agenda_medico")
    else:
        F=forms.modelform_factory(BloqueioAgenda,fields=["data_hora_inicio","data_hora_fim","justificativa","tipo"]); form=F()
    return render(request,"portal/form.html",{"form":form,"titulo":"Solicitar bloqueio/alteração de horário","voltar":reverse("portal_agenda_medico")})
@allowed(*ADMIN)
def bloqueios(request):
    return _list(request,"Solicitações de bloqueio",BloqueioAgenda.objects.select_related("agenda__medico__usuario"),{"Médico":"agenda__medico__usuario__nome","Início":"data_hora_inicio","Fim":"data_hora_fim","Tipo":"tipo","Status":"status"},filters=["agenda__medico__usuario__nome","status","tipo"])
@allowed(*ADMIN)
def bloqueio_decidir(request,pk,status):
    b=get_object_or_404(BloqueioAgenda,pk=pk)
    if status in ("APROVADO","REJEITADO") and request.method=="POST":
        b.status=status; b.save(update_fields=["status"]); messages.success(request,"Solicitação atualizada.")
    return redirect("portal_bloqueios")

REGISTRY = {
 "paciente": (Paciente, ["usuario","plano_medico"], "Pacientes"),
 "medico": (Medico, ["usuario","crm","rqe","especialidade"], "Médicos"),
 "especialidade": (Especialidade, ["nome","tempo_medio_consulta"], "Especialidades"),
 "agenda": (Agenda, ["medico"], "Agendas"),
 "disponibilidade": (Disponibilidade, ["agenda","dia_semana","horario_inicio","horario_fim"], "Disponibilidades"),
 "bloqueio": (BloqueioAgenda, ["agenda","data_hora_inicio","data_hora_fim","justificativa","tipo","status"], "Bloqueios"),
 "prontuario": (Prontuario, ["consulta","anamnese","diagnostico","observacoes"], "Prontuários"),
 "exame": (Exame, ["prontuario","nome","descricao","data_solicitacao"], "Exames"),
 "receita": (Receita, ["prontuario","descricao"], "Receitas"),
 "consulta": (Consulta, ["paciente","medico","data_hora","status"], "Consultas"),
}
@login_required
def registro_detalhe(request, tipo, pk):
    if tipo not in REGISTRY: return redirect("inicio")
    if tipo in ("prontuario", "exame", "receita") and request.user.tipo_usuario != Usuario.TipoUsuario.ADMINISTRADOR: return redirect("inicio")
    model, fields, title=REGISTRY[tipo]
    obj=get_object_or_404(model,pk=pk)
    if request.user.tipo_usuario not in ADMIN:
        if tipo=="disponibilidade" and request.user.tipo_usuario==Usuario.TipoUsuario.MEDICO and obj.agenda.medico.usuario_id==request.user.id: pass
        elif tipo=="bloqueio" and request.user.tipo_usuario==Usuario.TipoUsuario.MEDICO and obj.agenda.medico.usuario_id==request.user.id: pass
        elif tipo=="consulta" and request.user.tipo_usuario==Usuario.TipoUsuario.PACIENTE and obj.paciente.usuario_id==request.user.id: pass
        elif tipo=="consulta" and request.user.tipo_usuario==Usuario.TipoUsuario.MEDICO and obj.medico.usuario_id==request.user.id: pass
        else: return redirect("inicio")
    values=[(f.replace("_"," ").title(),str(getattr(obj,f))) for f in fields]
    return render(request,"portal/detalhe.html",{"titulo":title[:-1] if title.endswith("s") else title,"objeto":obj,"valores":values,"tipo":tipo,"can_manage":request.user.tipo_usuario in ADMIN})
@allowed(*ADMIN)
def registro_editar(request,tipo,pk):
    if tipo not in REGISTRY: return redirect("inicio")
    if tipo in ("prontuario", "exame", "receita") and request.user.tipo_usuario != Usuario.TipoUsuario.ADMINISTRADOR: return redirect("inicio")
    model,fields,title=REGISTRY[tipo]
    obj=get_object_or_404(model,pk=pk)
    F=forms.modelform_factory(model,fields=fields)
    form=F(request.POST or None,instance=obj)
    for f in form.fields.values(): f.widget.attrs["class"]="form-select" if isinstance(f.widget,forms.Select) else "form-control"
    if request.method=="POST" and form.is_valid():
        form.save(); messages.success(request,"Registro atualizado."); return redirect("portal_registro_detalhe",tipo,pk)
    return render(request,"portal/form.html",{"form":form,"titulo":"Editar "+title.lower(),"voltar":reverse("portal_registro_detalhe",args=[tipo,pk])})
@allowed(*ADMIN)
@require_POST
def registro_excluir(request,tipo,pk):
    if tipo not in REGISTRY: return redirect("inicio")
    if tipo in ("prontuario", "exame", "receita") and request.user.tipo_usuario != Usuario.TipoUsuario.ADMINISTRADOR: return redirect("inicio")
    model,fields,title=REGISTRY[tipo]
    obj=get_object_or_404(model,pk=pk); obj.delete()
    messages.success(request,"Registro excluído.")
    return redirect("portal_home")

@allowed(*ADMIN)
def registros_lista(request,tipo):
    if tipo not in REGISTRY: return redirect("portal_home")
    if tipo in ("prontuario", "exame", "receita") and request.user.tipo_usuario != Usuario.TipoUsuario.ADMINISTRADOR: return redirect("inicio")
    model, fields, title=REGISTRY[tipo]
    qs=model.objects.all()
    search_fields=[]
    for field in fields:
        try:
            f=model._meta.get_field(field)
            if f.get_internal_type() in ("CharField","TextField"): search_fields.append(field)
        except Exception: pass
    if not search_fields: search_fields=[fields[0]]
    return _list(request,title,qs,{f.replace("_"," ").title():f for f in fields},create_url=f"/portal/registros/{tipo}/novo/",filters=search_fields)
@allowed(*ADMIN)
def registro_novo(request,tipo):
    if tipo not in REGISTRY: return redirect("portal_home")
    if tipo in ("prontuario", "exame", "receita") and request.user.tipo_usuario != Usuario.TipoUsuario.ADMINISTRADOR: return redirect("inicio")
    model, fields, title=REGISTRY[tipo]
    F=forms.modelform_factory(model,fields=fields)
    form=F(request.POST or None)
    for f in form.fields.values(): f.widget.attrs["class"]="form-select" if isinstance(f.widget,forms.Select) else "form-control"
    if request.method=="POST" and form.is_valid():
        form.save(); messages.success(request,"Registro cadastrado."); return redirect("portal_registros_lista",tipo)
    return render(request,"portal/form.html",{"form":form,"titulo":"Novo(a) "+title.lower(),"voltar":reverse("portal_registros_lista",args=[tipo])})


@login_required
@allowed(Usuario.TipoUsuario.MEDICO)
def medico_solicitar_alteracao(request):
    agenda = get_object_or_404(Agenda, medico__usuario=request.user)
    if request.method == "POST":
        F = forms.modelform_factory(
            SolicitacaoDisponibilidade,
            fields=["disponibilidade", "dia_semana", "horario_inicio", "horario_fim", "justificativa"],
            widgets={
                "horario_inicio": forms.TimeInput(attrs={"type": "time"}),
                "horario_fim": forms.TimeInput(attrs={"type": "time"}),
            },
        )
        form = F(request.POST)
        form.fields["disponibilidade"].queryset = Disponibilidade.objects.filter(agenda=agenda)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.agenda = agenda
            try:
                solicitacao.full_clean()
                solicitacao.save()
            except Exception as error:
                form.add_error(None, str(error))
            else:
                messages.success(request, "Solicitação de alteração enviada para análise.")
                return redirect("portal_agenda_medico")
    else:
        F = forms.modelform_factory(
            SolicitacaoDisponibilidade,
            fields=["disponibilidade", "dia_semana", "horario_inicio", "horario_fim", "justificativa"],
            widgets={
                "horario_inicio": forms.TimeInput(attrs={"type": "time"}),
                "horario_fim": forms.TimeInput(attrs={"type": "time"}),
            },
        )
        form = F()
        form.fields["disponibilidade"].queryset = Disponibilidade.objects.filter(agenda=agenda)
    return render(request, "portal/form.html", {
        "form": form,
        "titulo": "Solicitar alteração de disponibilidade",
        "voltar": reverse("portal_agenda_medico"),
    })


@allowed(*ADMIN)
@require_POST
def gestao_analisar_alteracao(request, pk, decisao):
    solicitacao = get_object_or_404(
        SolicitacaoDisponibilidade.objects.select_related("disponibilidade", "agenda"),
        pk=pk,
    )
    if solicitacao.status != SolicitacaoDisponibilidade.Status.PENDENTE:
        messages.warning(request, "Esta solicitação já foi analisada.")
        return redirect("portal_bloqueios")
    if decisao == "aprovar":
        disponibilidade = solicitacao.disponibilidade
        disponibilidade.dia_semana = solicitacao.dia_semana
        disponibilidade.horario_inicio = solicitacao.horario_inicio
        disponibilidade.horario_fim = solicitacao.horario_fim
        try:
            disponibilidade.full_clean()
            disponibilidade.save()
        except Exception as error:
            messages.error(request, f"Não foi possível aprovar a alteração: {error}")
            return redirect("portal_bloqueios")
        solicitacao.status = SolicitacaoDisponibilidade.Status.APROVADA
    elif decisao == "rejeitar":
        solicitacao.status = SolicitacaoDisponibilidade.Status.REJEITADA
    else:
        messages.error(request, "Decisão inválida.")
        return redirect("portal_bloqueios")
    solicitacao.save(update_fields=["status"])
    messages.success(request, "Solicitação analisada.")
    return redirect("portal_bloqueios")


@allowed(*ADMIN)
@require_POST
def gestao_analisar_bloqueio(request, pk, decisao):
    bloqueio = get_object_or_404(BloqueioAgenda, pk=pk)
    if decisao == "aprovar":
        bloqueio.status = BloqueioAgenda.Status.APROVADO
    elif decisao == "rejeitar":
        bloqueio.status = BloqueioAgenda.Status.REJEITADO
    else:
        messages.error(request, "Decisão inválida.")
        return redirect("portal_bloqueios")
    bloqueio.save(update_fields=["status"])
    messages.success(request, "Solicitação de bloqueio analisada.")
    return redirect("portal_bloqueios")
