from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import date
from db import execute_query, execute_query_one, execute_insert, execute_update, DatabaseError

main_bp = Blueprint('main', __name__)



def nettoyer_telephone(tel):
    """Enlève tout sauf les chiffres d'un numéro de téléphone."""
    if not tel:
        return None
    return ''.join(c for c in tel if c.isdigit()) or None

# =============================================================================
# TABLEAU DE BORD
# =============================================================================

@main_bp.route('/tableau-de-bord')
def tableau_bord():

    commandes_retard = execute_query("select * from COMMANDE_EN_RETARD order by DATE_LIMITE_COMMANDE")
    commandes_en_cours = execute_query("select * from COMMANDE_EN_COURS order by DATE_LIMITE_COMMANDE nulls last")

    stats = {
        'nb_retard': len(commandes_retard),
        'nb_en_cours': len(commandes_en_cours)
    }
    
    return render_template('tableau_bord.html',
                          commandes_retard=commandes_retard,
                          commandes_en_cours=commandes_en_cours,
                          stats=stats,
                          recherche='')

@main_bp.route('/recherche', methods=['GET', 'POST'])
def recherche():
    recherche = request.args.get('recherche', "").strip()

    sql_retard = """
               select * from COMMANDE_EN_RETARD 
               where nom_compagnie_cli ilike %s or cast(NO_COMMANDE as text) = %s or cast(NO_CLIENT as text) = %s
               order by DATE_LIMITE_COMMANDE
           """
    sql_en_cours = """
               select * from COMMANDE_EN_COURS 
               where nom_compagnie_cli ilike %s or cast(NO_COMMANDE as text) = %s or cast(NO_CLIENT as text) = %s
               order by DATE_LIMITE_COMMANDE nulls last
           """
    sql_completee = """
           select * from COMMANDE_COMPLETEE 
           where nom_compagnie_cli ilike %s or cast(NO_COMMANDE as text) = %s or cast(NO_CLIENT as text) = %s
           order by DATE_LIMITE_COMMANDE nulls last
           """
    sql_annulee = """
        select * from COMMANDE_ANNULEE
        where nom_compagnie_cli ilike %s or cast(NO_COMMANDE as text) = %s or cast(NO_CLIENT as text) = %s
         order by DATE_LIMITE_COMMANDE nulls last
        """
    params = (f'%{recherche}%', recherche, recherche)
    recherche_commandes_retard = execute_query(sql_retard, params)
    recherche_commandes_en_cours = execute_query(sql_en_cours, params)  # VA FALLOIR AJOUTER MES COMMANDE_ANNULEE aussi
    recherche_commandes_completees = execute_query(sql_completee, params)
    recherche_commandes_annulees = execute_query(sql_annulee, params)

    recherche_stats = {
        'nb_retard': len(recherche_commandes_retard),
        'nb_en_cours': len(recherche_commandes_en_cours)
    }

    return render_template('recherche.html',
                           recherche_commandes_retard=recherche_commandes_retard,
                           recherche_commandes_en_cours=recherche_commandes_en_cours,
                           recherche_commandes_completees=recherche_commandes_completees,
                           recherche_commandes_annulees=recherche_commandes_annulees,
                           recherche_stats=recherche_stats,
                           recherche=recherche)


@main_bp.route('/commande/<int:no_commande>/completer', methods=['POST'])
def commande_completer_rapide(no_commande):
    """Marquer une commande comme complétée depuis le tableau de bord."""
    try:
        execute_update("update COMMANDE set STATUT_COMMANDE = 'COMPLETEE' where NO_COMMANDE = %s", (no_commande,))
        flash("Commande marquée comme complétée.", "success")
    except DatabaseError as e:
        flash(str(e), "danger")
    return redirect(url_for('main.tableau_bord'))


# =============================================================================
# API - VÉRIFICATION SIMILARITÉ CLIENT (TRIGRAMME)
# =============================================================================

@main_bp.route('/api/verifier-client', methods=['POST'])
def verifier_client():
    """Vérifie si un nom de client similaire existe déjà (trigramme)."""
    data = request.get_json()
    nom = data.get('nom', '').strip()
    
    if not nom or len(nom) < 3:
        return jsonify({'similaires': []})
    
    try:
        sql = """
            select NO_CLIENT, NOM_COMPAGNIE_CLI, similarity(NOM_COMPAGNIE_CLI, %s) as similarite
            from CLIENT
            where similarity(NOM_COMPAGNIE_CLI, %s) > 0.4
            order by similarity(NOM_COMPAGNIE_CLI, %s) desc
            limit 5
        """
        similaires = execute_query(sql, (nom, nom, nom))
        return jsonify({
            'similaires': [dict(s) for s in similaires]
        })
    except:
        return jsonify({'similaires': []})


# =============================================================================
# COMMANDE - DÉTAILS (readonly - bon de travail)
# =============================================================================

@main_bp.route('/commande/<int:no_commande>/details')
def commande_details(no_commande):
    sql = """
        select CMD.*, C.NOM_COMPAGNIE_CLI, C.PRENOM_CONTACT_CLI, C.NOM_CONTACT_CLI,
               C.ADRESSE_COMPAGNIE_CLI, C.VILLE_COMPAGNIE_CLI, C.CODE_POSTAL_COMPAGNIE_CLI,
               C.NUMERO_TELEPHONE_COMPAGNIE_CLI, TRA.TYPE_TRAVAIL, ST.NOM_SOUS_TRAITANT
        from COMMANDE CMD
        join CLIENT C on CMD.NO_CLIENT = C.NO_CLIENT
        left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
        left join SOUS_TRAITANT ST on CMD.NO_SOUS_TRAITANT = ST.NO_SOUS_TRAITANT
        where CMD.NO_COMMANDE = %s
    """
    commande = execute_query_one(sql, (no_commande,))
    
    if not commande:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('main.tableau_bord'))
    
    livraisons = execute_query("select * from LIVRAISON where NO_COMMANDE = %s order by DATE_LIVRAISON", (no_commande,))
    
    # Calculer coût total
    cout_total = (commande['cout_commande'] or 0) + (commande['cout_infographie'] or 0) + (commande['cout_sous_traitant'] or 0)
    cout_livraisons = sum(liv['cout_livraison'] or 0 for liv in livraisons)
    cout_total += cout_livraisons
    
    return render_template('commande_details.html',
                          commande=commande,
                          livraisons=livraisons,
                          cout_total=cout_total)


# =============================================================================
# COMMANDE - MODIFIER
# =============================================================================

@main_bp.route('/commande/<int:no_commande>/modifier', methods=['GET', 'POST'])
def commande_modifier(no_commande):
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'supprimer':
                execute_update("delete from LIVRAISON where NO_COMMANDE = %s", (no_commande,))
                execute_update("delete from COMMANDE where NO_COMMANDE = %s", (no_commande,))
                flash("Commande supprimée.", "success")
                return redirect(url_for('main.tableau_bord'))
            
            if action == 'completer':   #VERIFIER QUE C'EST LE BON NOM D'ACTION
                execute_update("update COMMANDE set STATUT_COMMANDE = 'COMPLETEE' where NO_COMMANDE = %s", (no_commande,))
                flash("Commande marquée comme complétée.", "success")
                return redirect(url_for('main.tableau_bord'))
            
            if action == 'annuler':
                notes = request.form.get('notes_annulation', '')
                execute_update("update COMMANDE set STATUT_COMMANDE = 'ANNULEE', NOTES_ANNULATION = %s where NO_COMMANDE = %s", (notes, no_commande))
                flash("Commande annulée.", "success")
                return redirect(url_for('main.tableau_bord'))
            
            return sauvegarder_commande(no_commande)
        except DatabaseError as e:
            flash(str(e), "danger")
    
    sql = """
        select CMD.*, C.NOM_COMPAGNIE_CLI, C.PRENOM_CONTACT_CLI, C.NOM_CONTACT_CLI,
               C.ADRESSE_COMPAGNIE_CLI, C.VILLE_COMPAGNIE_CLI, C.CODE_POSTAL_COMPAGNIE_CLI,
               C.NUMERO_TELEPHONE_COMPAGNIE_CLI
        from COMMANDE CMD
        join CLIENT C ON CMD.NO_CLIENT = C.NO_CLIENT
        where CMD.NO_COMMANDE = %s
    """
    commande = execute_query_one(sql, (no_commande,))
    
    if not commande:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('main.tableau_bord'))
    
    livraisons = execute_query("select * from LIVRAISON where NO_COMMANDE = %s order by DATE_LIVRAISON", (no_commande,))
    clients = execute_query("select * from CLIENT order by NOM_COMPAGNIE_CLI")
    types_travail = execute_query("select * from TYPE_TRAVAIL order by TYPE_TRAVAIL")
    sous_traitants = execute_query("select * from SOUS_TRAITANT order by NOM_SOUS_TRAITANT")
    
    return render_template('commande_form.html',
                          commande=commande,
                          livraisons=livraisons,
                          clients=clients,
                          types_travail=types_travail,
                          sous_traitants=sous_traitants,
                          today=date.today().isoformat(),
                          client_preselect=None)


# =============================================================================
# COMMANDE - NOUVELLE
# =============================================================================

@main_bp.route('/commande/nouveau', methods=['GET', 'POST'])
def commande_nouveau():
    if request.method == 'POST':
        try:
            return sauvegarder_commande(None)
        except DatabaseError as e:
            flash(str(e), "danger")
    
    # Vérifier si un client est pré-sélectionné
    no_client = request.args.get('client')
    client_preselect = None
    if no_client:
        client_preselect = execute_query_one("select * from CLIENT where NO_CLIENT = %s", (no_client,))
    
    clients = execute_query("select * from CLIENT order by NOM_COMPAGNIE_CLI")
    types_travail = execute_query("select * from TYPE_TRAVAIL order by TYPE_TRAVAIL")
    sous_traitants = execute_query("select * from SOUS_TRAITANT order by NOM_SOUS_TRAITANT")
    
    return render_template('commande_form.html',
                          commande=None,
                          livraisons=[],
                          clients=clients,
                          types_travail=types_travail,
                          sous_traitants=sous_traitants,
                          today=date.today().isoformat(),
                          client_preselect=client_preselect)


def sauvegarder_commande(no_commande):
    form = request.form
    
    # Gérer le client - IMPORTANT: vérifier si no_client existe et n'est pas vide
    no_client = form.get('no_client', '').strip()
    
    if not no_client:
        # Créer nouveau client seulement si no_client est vide
        nom_compagnie = form.get('nom_compagnie_cli', '').strip()
        if not nom_compagnie:
            raise DatabaseError("Le nom de la compagnie est requis.")
        
        sql_client = """
            insert into CLIENT (NOM_COMPAGNIE_CLI, PRENOM_CONTACT_CLI, NOM_CONTACT_CLI,
                               ADRESSE_COMPAGNIE_CLI, VILLE_COMPAGNIE_CLI, 
                               CODE_POSTAL_COMPAGNIE_CLI, NUMERO_TELEPHONE_COMPAGNIE_CLI)
            values (%s, %s, %s, %s, %s, %s, %s)
            returning NO_CLIENT
        """
        no_client = execute_insert(sql_client, (
            nom_compagnie,
            form.get('prenom_contact_cli') or None,
            form.get('nom_contact_cli') or None,
            form.get('adresse_compagnie_cli') or None,
            form.get('ville_compagnie_cli') or None,
            form.get('code_postal_compagnie_cli') or None,
            nettoyer_telephone(form.get('numero_telephone_compagnie_cli')) or None
        ))
    
    # Gérer l'impression et les contraintes
    est_impression = form.get('est_une_impression') == 'on'
    
    if est_impression:
        recto_verso = form.get('recto_verso_impression') == 'true'
        type_impression = form.get('type_impression') or None
        type_encre_recto = form.get('type_encre_recto') or None
        type_encre_verso = form.get('type_encre_verso') if recto_verso else None
        
        # Validation pour respecter CHK_IMPRESSION_COHERENT
        if not type_encre_recto:
            raise DatabaseError("Pour une impression, le type d'encre recto est obligatoire.")
        if recto_verso and not type_encre_verso:
            raise DatabaseError("Pour une impression recto/verso, le type d'encre verso est obligatoire.")
    else:
        recto_verso = None
        type_impression = None
        type_encre_recto = None
        type_encre_verso = None
    
    no_dossier = form.get('no_dossier') or None
    no_sous_traitant = form.get('no_sous_traitant') or None
    
    if no_commande:
        sql = """
            update COMMANDE set
                NO_CLIENT = %s, NO_DOSSIER = %s, DATE_COMMANDE = %s, DATE_LIMITE_COMMANDE = %s,
                PO_CLIENT_COMMANDE = %s, QUANTITE_COMMANDE = %s, EST_UNE_IMPRESSION = %s,
                TYPE_IMPRESSION = %s, FORMAT_FINAL_IMPRESSION = %s, FORMAT_OUVERT_IMPRESSION = %s,
                RECTO_VERSO_IMPRESSION = %s, TYPE_ENCRE_RECTO = %s, TYPE_ENCRE_VERSO = %s,
                TYPE_PAPIER = %s, TYPE_FINITION = %s, NUMEROTAGE_FINITION_DEBUT = %s,
                NUMEROTAGE_FINITION_FIN = %s, NOTES_FINITION = %s, NOTES_COMMANDE = %s,
                NO_SOUS_TRAITANT = %s, PO_SOUS_TRAITANT = %s, COUT_COMMANDE = %s,
                COUT_INFOGRAPHIE = %s, COUT_SOUS_TRAITANT = %s
            where NO_COMMANDE = %s
        """
        params = (
            no_client, no_dossier,
            form.get('date_commande'),
            form.get('date_limite_commande') or None,
            form.get('po_client_commande') or None,
            int(form.get('quantite_commande')),
            est_impression,
            type_impression,
            form.get('format_final_impression') or None,
            form.get('format_ouvert_impression') or None,
            recto_verso,
            type_encre_recto,
            type_encre_verso,
            form.get('type_papier') or None,
            form.get('type_finition') or None,
            int(form.get('numerotage_finition_debut')) if form.get('numerotage_finition_debut') else None,
            int(form.get('numerotage_finition_fin')) if form.get('numerotage_finition_fin') else None,
            form.get('notes_finition') or None,
            form.get('notes_commande') or None,
            no_sous_traitant,
            form.get('po_sous_traitant') or None,
            float(form.get('cout_commande') or 0),
            float(form.get('cout_infographie')) if form.get('cout_infographie') else None,
            float(form.get('cout_sous_traitant')) if form.get('cout_sous_traitant') else None,
            no_commande
        )
        execute_update(sql, params)
        flash("Commande modifiée.", "success")
    else:
        sql = """
            insert into COMMANDE (
                NO_CLIENT, NO_DOSSIER, DATE_COMMANDE, DATE_LIMITE_COMMANDE,
                PO_CLIENT_COMMANDE, QUANTITE_COMMANDE, EST_UNE_IMPRESSION,
                TYPE_IMPRESSION, FORMAT_FINAL_IMPRESSION, FORMAT_OUVERT_IMPRESSION,
                RECTO_VERSO_IMPRESSION, TYPE_ENCRE_RECTO, TYPE_ENCRE_VERSO,
                TYPE_PAPIER, TYPE_FINITION, NUMEROTAGE_FINITION_DEBUT,
                NUMEROTAGE_FINITION_FIN, NOTES_FINITION, NOTES_COMMANDE,
                NO_SOUS_TRAITANT, PO_SOUS_TRAITANT, COUT_COMMANDE,
                COUT_INFOGRAPHIE, COUT_SOUS_TRAITANT
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning NO_COMMANDE
        """
        params = (
            no_client, no_dossier,
            form.get('date_commande'),
            form.get('date_limite_commande') or None,
            form.get('po_client_commande') or None,
            int(form.get('quantite_commande')),
            est_impression,
            type_impression,
            form.get('format_final_impression') or None,
            form.get('format_ouvert_impression') or None,
            recto_verso,
            type_encre_recto,
            type_encre_verso,
            form.get('type_papier') or None,
            form.get('type_finition') or None,
            int(form.get('numerotage_finition_debut')) if form.get('numerotage_finition_debut') else None,
            int(form.get('numerotage_finition_fin')) if form.get('numerotage_finition_fin') else None,
            form.get('notes_finition') or None,
            form.get('notes_commande') or None,
            no_sous_traitant,
            form.get('po_sous_traitant') or None,
            float(form.get('cout_commande') or 0),
            float(form.get('cout_infographie')) if form.get('cout_infographie') else None,
            float(form.get('cout_sous_traitant')) if form.get('cout_sous_traitant') else None
        )
        no_commande = execute_insert(sql, params)
        flash(f"Commande #{no_commande} créée.", "success")
    
    # Ajouter livraison si remplie
    if form.get('livraison_quantite'):
        sql_liv = """
            insert into LIVRAISON (NO_COMMANDE, NO_BON_LIVRAISON, DATE_LIVRAISON, QUANTITE_LIVRAISON,
                                   ADRESSE_LIVRAISON, VILLE_LIVRAISON, CODE_POSTAL_LIVRAISON,
                                   NOTES_LIVRAISON, COUT_LIVRAISON)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_insert(sql_liv, (
            no_commande,
            int(form.get('livraison_no_bon')) if form.get('livraison_no_bon') else None,
            form.get('livraison_date') or None,
            int(form.get('livraison_quantite')),
            form.get('livraison_adresse') or None,
            form.get('livraison_ville') or None,
            form.get('livraison_code_postal') or None,
            form.get('livraison_notes') or None,
            float(form.get('livraison_cout')) if form.get('livraison_cout') else 0
        ))
    
    return redirect(url_for('main.commande_details', no_commande=no_commande))


@main_bp.route('/livraison/<int:no_livraison>/supprimer')
def supprimer_livraison(no_livraison):
    try:
        liv = execute_query_one("SELECT NO_COMMANDE FROM LIVRAISON WHERE NO_LIVRAISON = %s", (no_livraison,))
        if liv:
            execute_update("DELETE FROM LIVRAISON WHERE NO_LIVRAISON = %s", (no_livraison,))
            flash("Livraison supprimée.", "success")
            return redirect(url_for('main.commande_modifier', no_commande=liv['no_commande']))
    except DatabaseError as e:
        flash(str(e), "danger")
    return redirect(url_for('main.tableau_bord'))


# =============================================================================
# CLIENTS
# =============================================================================

@main_bp.route('/clients')
def clients():
    recherche = request.args.get('recherche', '').strip()
    
    if recherche:
        clients_list = execute_query(
            "select * from CLIENT where NOM_COMPAGNIE_CLI ilike %s order by NOM_COMPAGNIE_CLI",
            (f'%{recherche}%',)
        )
    else:
        clients_list = execute_query("select * from CLIENT order by NOM_COMPAGNIE_CLI")
    
    return render_template('clients.html', clients=clients_list, recherche=recherche)


@main_bp.route('/clients/<int:no_client>')
def client_detail(no_client):
    client = execute_query_one("select * from CLIENT where NO_CLIENT = %s", (no_client,))
    
    if not client:
        flash("Client introuvable.", "danger")
        return redirect(url_for('main.clients'))
    
    commandes = execute_query("""
        select CMD.*, TRA.TYPE_TRAVAIL
        from COMMANDE CMD
        left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
        where CMD.NO_CLIENT = %s
        order by CMD.DATE_COMMANDE desc
    """, (no_client,))
    
    return render_template('client_detail.html', client=client, commandes=commandes)


@main_bp.route('/clients/nouveau', methods=['POST'])
def client_nouveau():
    form = request.form
    try:
        execute_insert("""
            insert into CLIENT (NOM_COMPAGNIE_CLI, PRENOM_CONTACT_CLI, NOM_CONTACT_CLI,
                               ADRESSE_COMPAGNIE_CLI, VILLE_COMPAGNIE_CLI,
                               CODE_POSTAL_COMPAGNIE_CLI, NUMERO_TELEPHONE_COMPAGNIE_CLI)
            values (%s, %s, %s, %s, %s, %s, %s)
        """, (
            form.get('nom_compagnie_cli'),
            form.get('prenom_contact_cli') or None,
            form.get('nom_contact_cli') or None,
            form.get('adresse_compagnie_cli') or None,
            form.get('ville_compagnie_cli') or None,
            form.get('code_postal_compagnie_cli') or None,
            nettoyer_telephone(form.get('numero_telephone_compagnie_cli')) or None
        ))
        flash("Client créé.", "success")
    except DatabaseError as e:
        flash(str(e), "danger")
    return redirect(url_for('main.clients'))


@main_bp.route('/clients/<int:no_client>/supprimer', methods=['POST'])
def client_supprimer(no_client):
    """Supprimer un client (seulement s'il n'a pas de commandes)."""
    try:
        # Vérifier s'il a des commandes
        commandes = execute_query("select count(*) as nb from COMMANDE where NO_CLIENT = %s", (no_client,))
        if commandes and commandes[0]['nb'] > 0:
            flash("Impossible de supprimer ce client: il a des commandes associées.", "danger")
        else:
            execute_update("delete from CLIENT where NO_CLIENT = %s", (no_client,))
            flash("Client supprimé.", "success")
    except DatabaseError as e:
        flash(str(e), "danger")
    return redirect(url_for('main.clients'))


# =============================================================================
# PARAMÈTRES
# =============================================================================

@main_bp.route('/parametres', methods=['GET', 'POST'])
def parametres():
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'ajouter_type':
                nom = request.form.get('type_travail', '').strip()
                if nom:
                    execute_insert("insert into TYPE_TRAVAIL (TYPE_TRAVAIL) values (%s)", (nom,))
                    flash(f"Type '{nom}' ajouté.", "success")
            
            elif action == 'supprimer_type':
                no_dossier = request.form.get('no_dossier')
                execute_update("delete from TYPE_TRAVAIL where NO_DOSSIER = %s", (no_dossier,))
                flash("Type supprimé.", "success")
            
            elif action == 'ajouter_sous_traitant':
                nom = request.form.get('nom_sous_traitant', '').strip()
                if nom:
                    execute_insert("insert into SOUS_TRAITANT (NOM_SOUS_TRAITANT) values (%s)", (nom,))
                    flash(f"Sous-traitant '{nom}' ajouté.", "success")
            
            elif action == 'supprimer_sous_traitant':
                execute_update("delete from SOUS_TRAITANT where NO_SOUS_TRAITANT = %s", (request.form.get('no_sous_traitant'),))
                flash("Sous-traitant supprimé.", "success")
        
        except DatabaseError as e:
            flash(str(e), "danger")
        
        return redirect(url_for('main.parametres'))
    
    types_travail = execute_query("select * from TYPE_TRAVAIL order by TYPE_TRAVAIL")
    sous_traitants = execute_query("select * from SOUS_TRAITANT order by NOM_SOUS_TRAITANT")
    
    return render_template('parametres.html', types_travail=types_travail, sous_traitants=sous_traitants)


@main_bp.route('/client/<int:no_client>/modifier', methods=['GET', 'POST'])
def client_modifier(no_client):  # ✅ Bon nom de paramètre

    # Si formulaire soumis (POST)
    if request.method == 'POST':
        try:
            form = request.form
            sql = """
                UPDATE CLIENT SET
                    NOM_COMPAGNIE_CLI = %s,
                    PRENOM_CONTACT_CLI = %s,
                    NOM_CONTACT_CLI = %s,
                    ADRESSE_COMPAGNIE_CLI = %s,
                    VILLE_COMPAGNIE_CLI = %s,
                    CODE_POSTAL_COMPAGNIE_CLI = %s,
                    NUMERO_TELEPHONE_COMPAGNIE_CLI = %s
                WHERE NO_CLIENT = %s
            """
            execute_update(sql, (
                form.get('nom_compagnie_cli'),
                form.get('prenom_contact_cli') or None,
                form.get('nom_contact_cli') or None,
                form.get('adresse_compagnie_cli') or None,
                form.get('ville_compagnie_cli') or None,
                form.get('code_postal_compagnie_cli') or None,
                nettoyer_telephone(form.get('numero_telephone_compagnie_cli')) or None,
                no_client
            ))
            flash("Client modifié.", "success")
            return redirect(url_for('main.client_detail', no_client=no_client))
        except DatabaseError as e:
            flash(str(e), "danger")

    # Charger les données du client (GET)
    client = execute_query_one("SELECT * FROM CLIENT WHERE NO_CLIENT = %s", (no_client,))

    if not client:
        flash("Client introuvable.", "danger")
        return redirect(url_for('main.clients'))

    # Charger les commandes du client
    commandes = execute_query("""
        SELECT CMD.*, TRA.TYPE_TRAVAIL
        FROM COMMANDE CMD
        LEFT JOIN TYPE_TRAVAIL TRA ON CMD.NO_DOSSIER = TRA.NO_DOSSIER
        WHERE CMD.NO_CLIENT = %s
        ORDER BY CMD.DATE_COMMANDE DESC
    """, (no_client,))

    return render_template('clients_modification.html',
                           client=client,
                           commandes=commandes)