create extension if not exists pg_trgm; 
/*
drop view if exists COMMANDE_COMPLETEE;
drop view if exists COMMANDE_EN_COURS;
drop view if exists COMMANDE_EN_RETARD;
drop view if exists COMMANDE_ANNULEE;
drop view if exists COMMANDE_ARCHIVEE;

drop table if exists LIVRAISON;
drop table if exists LIVRAISON_ARCHIVE;
drop table if exists COMMANDE;
drop table if exists COMMANDE_ARCHIVE;
drop table if exists CLIENT;
drop table if exists TYPE_TRAVAIL;
drop table if exists SOUS_TRAITANT;

drop sequence if exists NO_CLIENT_SEQ;
drop sequence if exists NO_COMMANDE_SEQ;
drop sequence if exists NO_LIVRAISON_SEQ;
drop sequence if exists NO_BON_LIVRAISON_SEQ;
drop sequence if exists NO_SOUS_TRAITANT_SEQ;
drop sequence if exists NO_DOSSIER_SEQ;
*/

-- ========================= --
-- CREATION DE MES SEQUENCES --
-- ========================= --


create sequence NO_CLIENT_SEQ start with 1000 increment by 1; 
create sequence NO_COMMANDE_SEQ start with 1 increment by 1;
create sequence NO_LIVRAISON_SEQ start with 1 increment by 1;
create sequence NO_BON_LIVRAISON_SEQ start with 1000 increment by 1;
create sequence NO_SOUS_TRAITANT_SEQ start with 1 increment by 1;
create sequence NO_DOSSIER_SEQ start with 1 increment by 1;


-- ====================== --
-- CREATION DE MES TABLES --
-- ====================== --


create table CLIENT (
	NO_CLIENT integer not null default nextval('NO_CLIENT_SEQ'),
	NOM_CONTACT_CLI varchar(50) null,
	PRENOM_CONTACT_CLI varchar(50) null,
	NOM_COMPAGNIE_CLI varchar(50) not null, 
	ADRESSE_COMPAGNIE_CLI varchar(100) null,
	VILLE_COMPAGNIE_CLI varchar(50) null,
	CODE_POSTAL_COMPAGNIE_CLI char(7) null,
	NUMERO_TELEPHONE_COMPAGNIE_CLI char(10) null, 
	
	constraint PK_CLIENT primary key (NO_CLIENT)
);

create table TYPE_TRAVAIL (
	NO_DOSSIER integer not null default nextval('NO_DOSSIER_SEQ'),
	TYPE_TRAVAIL varchar(50),

	constraint AK_TYPE_TRAVAIL unique (TYPE_TRAVAIL),
	constraint PK_TYPE_TRAVAIL primary key (NO_DOSSIER)
);

create table SOUS_TRAITANT (
	NO_SOUS_TRAITANT integer not null default nextval('NO_SOUS_TRAITANT_SEQ'),
	NOM_SOUS_TRAITANT varchar(50),
	
	constraint PK_SOUS_TRAITANT primary key (NO_SOUS_TRAITANT)
);

create table COMMANDE (
	NO_COMMANDE integer not null default nextval('NO_COMMANDE_SEQ'),
	NO_CLIENT integer not null,
	NO_DOSSIER integer null,
	DATE_COMMANDE date not null,
	DATE_LIMITE_COMMANDE date null,
	PO_CLIENT_COMMANDE varchar(50) null,
	QUANTITE_COMMANDE integer not null,
	EST_UNE_IMPRESSION boolean not null default true,
	TYPE_IMPRESSION varchar(100) null,
	FORMAT_FINAL_IMPRESSION varchar(50) null,
	FORMAT_OUVERT_IMPRESSION varchar(50) null,
	RECTO_VERSO_IMPRESSION bool null,
	TYPE_ENCRE_RECTO varchar(50) null,
	TYPE_ENCRE_VERSO varchar(50) null,
	TYPE_PAPIER varchar(100) null,
	TYPE_FINITION varchar(100) null,
	NUMEROTAGE_FINITION_DEBUT integer null,
	NUMEROTAGE_FINITION_FIN integer null,
	NOTES_FINITION varchar(500) null,
	NOTES_COMMANDE varchar(500) null,
	NO_SOUS_TRAITANT integer null,
	PO_SOUS_TRAITANT varchar(50) null,
	COUT_COMMANDE decimal(10,2) not null,
	COUT_INFOGRAPHIE decimal(10,2) null,
	COUT_SOUS_TRAITANT decimal(10,2) null,
	STATUT_COMMANDE varchar(20) default 'EN_COURS',
	NOTES_ANNULATION varchar(500) null,
	DATE_MODIFICATION timestamp null, 
	
	constraint FK_COMMANDE_NO_CLIENT
		foreign key (NO_CLIENT) references CLIENT(NO_CLIENT),
	constraint FK_COMMANDE_NO_DOSSIER
		foreign key (NO_DOSSIER) references TYPE_TRAVAIL(NO_DOSSIER),
	constraint FK_COMMANDE_NO_SOUS_TRAITANT
		foreign key (NO_SOUS_TRAITANT) references SOUS_TRAITANT(NO_SOUS_TRAITANT),
	constraint PK_COMMANDE primary key (NO_COMMANDE),

	constraint CHK_NUMEROTAGE_COHERENT check (
		(NUMEROTAGE_FINITION_DEBUT is null and NUMEROTAGE_FINITION_FIN is null)
		or
		(NUMEROTAGE_FINITION_DEBUT is not null and NUMEROTAGE_FINITION_FIN is not null and NUMEROTAGE_FINITION_FIN >= NUMEROTAGE_FINITION_DEBUT)
	),

	constraint CHK_IMPRESSION_COHERENT check (
		(EST_UNE_IMPRESSION = true
			and RECTO_VERSO_IMPRESSION = false
			and TYPE_ENCRE_RECTO is not null
			and TYPE_ENCRE_VERSO is null)
		or
		(EST_UNE_IMPRESSION = true
			and RECTO_VERSO_IMPRESSION = true
			and TYPE_ENCRE_RECTO is not null
			and TYPE_ENCRE_VERSO is not null)
		or
		(EST_UNE_IMPRESSION = false
			and RECTO_VERSO_IMPRESSION is null
			and TYPE_ENCRE_RECTO is null 
			and TYPE_ENCRE_VERSO is null
			and TYPE_IMPRESSION is null)
	),

	constraint CHK_DATES_COHERENTES check (
		(DATE_LIMITE_COMMANDE is null or DATE_COMMANDE <= DATE_LIMITE_COMMANDE)
	),

	constraint CHK_SOUS_TRAITANT_COHERENT check (
		(NO_SOUS_TRAITANT is null and (COUT_SOUS_TRAITANT is null or COUT_SOUS_TRAITANT = 0.00))
		or
		(NO_SOUS_TRAITANT is not null and (COUT_SOUS_TRAITANT is null or COUT_SOUS_TRAITANT >= 0.00))
	),

	constraint CHK_STATUT_VALIDE check (
		STATUT_COMMANDE in ('EN_COURS', 'COMPLETEE', 'ANNULEE')
	)
);

create table LIVRAISON (
	NO_LIVRAISON integer not null default nextval('NO_LIVRAISON_SEQ'),
	NO_BON_LIVRAISON integer null default nextval('NO_BON_LIVRAISON_SEQ'),
	NO_COMMANDE integer not null,
	NOTES_LIVRAISON varchar(500),
	QUANTITE_LIVRAISON integer,
	DATE_LIVRAISON date null,
	ADRESSE_LIVRAISON varchar(100) null,
	VILLE_LIVRAISON varchar(50) null,
	CODE_POSTAL_LIVRAISON char(7) null,
	COUT_LIVRAISON decimal(10,2) null, 
	
	constraint FK_LIVRAISON_NO_COMMANDE
		foreign key (NO_COMMANDE) references COMMANDE(NO_COMMANDE),	
	constraint PK_LIVRAISON primary key (NO_LIVRAISON)
);


-- ================= --
-- TABLES D'ARCHIVES --
-- ================= --


create table COMMANDE_ARCHIVE (
	NO_COMMANDE integer not null,
	NO_CLIENT integer not null,
	NO_DOSSIER integer null,
	DATE_COMMANDE date not null,
	DATE_LIMITE_COMMANDE date null,
	PO_CLIENT_COMMANDE varchar(50) null,
	QUANTITE_COMMANDE integer not null,
	EST_UNE_IMPRESSION boolean not null default true,
	TYPE_IMPRESSION varchar(100) null,
	FORMAT_FINAL_IMPRESSION varchar(50) null,
	FORMAT_OUVERT_IMPRESSION varchar(50) null,
	RECTO_VERSO_IMPRESSION bool null,
	TYPE_ENCRE_RECTO varchar(50) null,
	TYPE_ENCRE_VERSO varchar(50) null,
	TYPE_PAPIER varchar(100) null,
	TYPE_FINITION varchar(100) null,
	NUMEROTAGE_FINITION_DEBUT integer null,
	NUMEROTAGE_FINITION_FIN integer null,
	NOTES_FINITION varchar(500) null,
	NOTES_COMMANDE varchar(500) null,
	NO_SOUS_TRAITANT integer null,
	PO_SOUS_TRAITANT varchar(50) null,
	COUT_COMMANDE decimal(10,2) not null,
	COUT_INFOGRAPHIE decimal(10,2) null,
	COUT_SOUS_TRAITANT decimal(10,2) null,
	STATUT_COMMANDE varchar (20) not null,
	NOTES_ANNULATION varchar (500) null,
	DATE_MODIFICATION timestamp null,
	
	constraint PK_ARCHIVE_COMMANDE primary key (NO_COMMANDE)
);

create table LIVRAISON_ARCHIVE (
	NO_LIVRAISON integer not null,
	NO_BON_LIVRAISON integer null,
	NO_COMMANDE integer not null,
	NOTES_LIVRAISON varchar(500),
	QUANTITE_LIVRAISON integer,
	DATE_LIVRAISON date null,
	ADRESSE_LIVRAISON varchar(100) null,
	VILLE_LIVRAISON varchar(50) null,
	CODE_POSTAL_LIVRAISON char(7) null,
	COUT_LIVRAISON decimal(10,2) null, 
	
	constraint FK_ARCHIVE_LIVRAISON_NO_COMMANDE
		foreign key (NO_COMMANDE) references COMMANDE_ARCHIVE(NO_COMMANDE),	
	constraint PK_ARCHIVE_LIVRAISON primary key (NO_LIVRAISON)
);


-- =================== --
-- CREATIONS DES VIEWS --
-- =================== --


--view commande completee
create or replace view COMMANDE_COMPLETEE as 
select C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL, CMD.NO_COMMANDE, CMD.QUANTITE_COMMANDE, CMD.DATE_COMMANDE, CMD.DATE_LIMITE_COMMANDE, CMD.COUT_COMMANDE + coalesce(CMD.COUT_INFOGRAPHIE,0) + coalesce(sum(LIV.COUT_LIVRAISON), 0)  as COUT_TOTAL_COMMANDE, CMD.STATUT_COMMANDE
	from COMMANDE CMD 
	join CLIENT C on CMD.NO_CLIENT = C.NO_CLIENT  
	left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
	left join LIVRAISON LIV on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		where CMD.STATUT_COMMANDE = 'COMPLETEE'
		group by CMD.NO_COMMANDE, C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL
		order by C.NOM_COMPAGNIE_CLI, DATE_COMMANDE asc; 
	
--view commande en cours
create or replace view COMMANDE_EN_COURS as 
select C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL, CMD.NO_COMMANDE, CMD.QUANTITE_COMMANDE, CMD.DATE_COMMANDE, CMD.DATE_LIMITE_COMMANDE, CMD.COUT_COMMANDE + coalesce(CMD.COUT_INFOGRAPHIE,0) + coalesce(sum(LIV.COUT_LIVRAISON), 0)  as COUT_TOTAL_COMMANDE, CMD.STATUT_COMMANDE 
	from COMMANDE CMD 
	join CLIENT C on CMD.NO_CLIENT = C.NO_CLIENT   
	left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
	left join LIVRAISON LIV on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		where CMD.STATUT_COMMANDE = 'EN_COURS' and (CMD.DATE_LIMITE_COMMANDE is null or current_date <= CMD.DATE_LIMITE_COMMANDE)
		group by CMD.NO_COMMANDE, C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL
		order by C.NOM_COMPAGNIE_CLI, DATE_COMMANDE asc; 
	
--view commande en retard
create or replace view COMMANDE_EN_RETARD as 
select C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL, CMD.NO_COMMANDE, CMD.QUANTITE_COMMANDE, CMD.DATE_COMMANDE, CMD.DATE_LIMITE_COMMANDE, CMD.COUT_COMMANDE + coalesce(CMD.COUT_INFOGRAPHIE,0) + coalesce(sum(LIV.COUT_LIVRAISON), 0)  as COUT_TOTAL_COMMANDE, CMD.STATUT_COMMANDE
	from COMMANDE CMD 
	join CLIENT C on CMD.NO_CLIENT = C.NO_CLIENT    
	left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
	left join LIVRAISON LIV on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		where CMD.STATUT_COMMANDE = 'EN_COURS' and CMD.DATE_LIMITE_COMMANDE is not null and current_date > CMD.DATE_LIMITE_COMMANDE
		group by CMD.NO_COMMANDE, C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL
		order by C.NOM_COMPAGNIE_CLI, DATE_COMMANDE asc; 

--view commande annulee 
create or replace view COMMANDE_ANNULEE as 
select C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL, CMD.NO_COMMANDE, CMD.QUANTITE_COMMANDE, CMD.DATE_COMMANDE, CMD.DATE_LIMITE_COMMANDE, CMD.COUT_COMMANDE + coalesce(CMD.COUT_INFOGRAPHIE,0) + coalesce(sum(LIV.COUT_LIVRAISON), 0)  as COUT_TOTAL_COMMANDE, CMD.STATUT_COMMANDE  
	from COMMANDE CMD 
	join CLIENT C on CMD.NO_CLIENT = C.NO_CLIENT    
	left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
	left join LIVRAISON LIV on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		where CMD.STATUT_COMMANDE = 'ANNULEE'
		group by CMD.NO_COMMANDE, C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL
		order by C.NOM_COMPAGNIE_CLI, DATE_COMMANDE asc; 
		
-- View commandes archivees
create or replace view COMMANDE_ARCHIVEE as 
select C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL, CMD.NO_COMMANDE, CMD.QUANTITE_COMMANDE, CMD.DATE_COMMANDE, CMD.DATE_LIMITE_COMMANDE, CMD.COUT_COMMANDE + coalesce(CMD.COUT_INFOGRAPHIE, 0) + coalesce(sum(LIV.COUT_LIVRAISON), 0) as COUT_TOTAL_COMMANDE, STATUT_COMMANDE
	from COMMANDE_ARCHIVE CMD 
	join CLIENT C on CMD.NO_CLIENT = C.NO_CLIENT  
	left join TYPE_TRAVAIL TRA on CMD.NO_DOSSIER = TRA.NO_DOSSIER
	left join LIVRAISON_ARCHIVE LIV on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		group by CMD.NO_COMMANDE, C.NOM_COMPAGNIE_CLI, C.NO_CLIENT, TRA.TYPE_TRAVAIL
		order by STATUT_COMMANDE desc, C.NOM_COMPAGNIE_CLI, CMD.DATE_COMMANDE asc;

	
-- ======= --
-- TRIGGER --
-- ======= --


create or replace function TRG_DATE_MODIFICATION()
returns trigger
language plpgsql
as $$
begin
	 new.DATE_MODIFICATION = current_timestamp;
	return new;
end;
$$;

create trigger TRG_COMMANDE_MODIFICATION
before update on COMMANDE
for each row
execute function TRG_DATE_MODIFICATION();


-- ========= --
-- PROCEDURE --
-- ========= --


/*Creation d'une procedure permettant d'archiver les commandes vieille de 1 an et demi et completees
ou les commandes annulee vieille de 1 mois*/
create or replace procedure SP_ARCHIVER_COMMANDES_ET_LIVRAISONS()
language plpgsql
as $$
declare
	V_DATE_COMPLETEE date := current_date - interval '16 months';
	V_DATE_ANNULEE date := current_date - interval '1 month';
begin 

--Archivage commande completee
	-- Archivage des livraisons
	insert into LIVRAISON_ARCHIVE (NO_LIVRAISON, NO_BON_LIVRAISON, NO_COMMANDE, NOTES_LIVRAISON, QUANTITE_LIVRAISON, DATE_LIVRAISON, ADRESSE_LIVRAISON, VILLE_LIVRAISON, CODE_POSTAL_LIVRAISON, COUT_LIVRAISON)
		select LIV.NO_LIVRAISON, LIV.NO_BON_LIVRAISON, LIV.NO_COMMANDE, LIV.NOTES_LIVRAISON, LIV.QUANTITE_LIVRAISON, LIV.DATE_LIVRAISON, LIV.ADRESSE_LIVRAISON, LIV.VILLE_LIVRAISON, LIV.CODE_POSTAL_LIVRAISON, LIV.COUT_LIVRAISON
		from LIVRAISON LIV
		join COMMANDE CMD on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		where CMD.DATE_COMMANDE <= V_DATE_COMPLETEE and CMD.STATUT_COMMANDE = 'COMPLETEE';
		
	-- Suppression des livraisons archivees	
	delete from LIVRAISON 
		where NO_COMMANDE in (
		select NO_COMMANDE from COMMANDE where DATE_COMMANDE <= V_DATE_COMPLETEE and STATUT_COMMANDE = 'COMPLETEE'
		); 

	-- Archivage des commandes
	insert into COMMANDE_ARCHIVE (NO_COMMANDE, NO_CLIENT, NO_DOSSIER, DATE_COMMANDE, DATE_LIMITE_COMMANDE, PO_CLIENT_COMMANDE, QUANTITE_COMMANDE, EST_UNE_IMPRESSION, TYPE_IMPRESSION, FORMAT_FINAL_IMPRESSION, FORMAT_OUVERT_IMPRESSION, RECTO_VERSO_IMPRESSION, TYPE_ENCRE_RECTO, TYPE_ENCRE_VERSO, TYPE_PAPIER, TYPE_FINITION, NUMEROTAGE_FINITION_DEBUT, NUMEROTAGE_FINITION_FIN, NOTES_FINITION, NOTES_COMMANDE, NO_SOUS_TRAITANT, PO_SOUS_TRAITANT, COUT_COMMANDE, COUT_INFOGRAPHIE, COUT_SOUS_TRAITANT, STATUT_COMMANDE, NOTES_ANNULATION, DATE_MODIFICATION)
		select NO_COMMANDE, NO_CLIENT, NO_DOSSIER, DATE_COMMANDE, DATE_LIMITE_COMMANDE, PO_CLIENT_COMMANDE, QUANTITE_COMMANDE, EST_UNE_IMPRESSION, TYPE_IMPRESSION, FORMAT_FINAL_IMPRESSION, FORMAT_OUVERT_IMPRESSION, RECTO_VERSO_IMPRESSION, TYPE_ENCRE_RECTO, TYPE_ENCRE_VERSO, TYPE_PAPIER, TYPE_FINITION, NUMEROTAGE_FINITION_DEBUT, NUMEROTAGE_FINITION_FIN, NOTES_FINITION, NOTES_COMMANDE, NO_SOUS_TRAITANT, PO_SOUS_TRAITANT, COUT_COMMANDE, COUT_INFOGRAPHIE, COUT_SOUS_TRAITANT, STATUT_COMMANDE, NOTES_ANNULATION, DATE_MODIFICATION
		from COMMANDE
		where DATE_COMMANDE <= V_DATE_COMPLETEE and STATUT_COMMANDE = 'COMPLETEE';

	-- Suppression des commandes archivees
	delete from COMMANDE where DATE_COMMANDE <= V_DATE_COMPLETEE and STATUT_COMMANDE = 'COMPLETEE';

--Archivage commande annulee
	-- Archivage des livraisons
	insert into LIVRAISON_ARCHIVE (NO_LIVRAISON, NO_BON_LIVRAISON, NO_COMMANDE, NOTES_LIVRAISON, QUANTITE_LIVRAISON, DATE_LIVRAISON, ADRESSE_LIVRAISON, VILLE_LIVRAISON, CODE_POSTAL_LIVRAISON, COUT_LIVRAISON)
		select LIV.NO_LIVRAISON, LIV.NO_BON_LIVRAISON, LIV.NO_COMMANDE, LIV.NOTES_LIVRAISON, LIV.QUANTITE_LIVRAISON, LIV.DATE_LIVRAISON, LIV.ADRESSE_LIVRAISON, LIV.VILLE_LIVRAISON, LIV.CODE_POSTAL_LIVRAISON, LIV.COUT_LIVRAISON
		from LIVRAISON LIV
		join COMMANDE CMD on LIV.NO_COMMANDE = CMD.NO_COMMANDE
		where CMD.DATE_COMMANDE <= V_DATE_ANNULEE and CMD.STATUT_COMMANDE = 'ANNULEE';
		
	-- Suppression des livraisons archivees	
	delete from LIVRAISON 
		where NO_COMMANDE in (
		select NO_COMMANDE from COMMANDE where DATE_COMMANDE <= V_DATE_ANNULEE and STATUT_COMMANDE = 'ANNULEE'
		); 

	-- Archivage des commandes
	insert into COMMANDE_ARCHIVE (NO_COMMANDE, NO_CLIENT, NO_DOSSIER, DATE_COMMANDE, DATE_LIMITE_COMMANDE, PO_CLIENT_COMMANDE, QUANTITE_COMMANDE, EST_UNE_IMPRESSION, TYPE_IMPRESSION, FORMAT_FINAL_IMPRESSION, FORMAT_OUVERT_IMPRESSION, RECTO_VERSO_IMPRESSION, TYPE_ENCRE_RECTO, TYPE_ENCRE_VERSO, TYPE_PAPIER, TYPE_FINITION, NUMEROTAGE_FINITION_DEBUT, NUMEROTAGE_FINITION_FIN, NOTES_FINITION, NOTES_COMMANDE, NO_SOUS_TRAITANT, PO_SOUS_TRAITANT, COUT_COMMANDE, COUT_INFOGRAPHIE, COUT_SOUS_TRAITANT, STATUT_COMMANDE, NOTES_ANNULATION, DATE_MODIFICATION)
		select NO_COMMANDE, NO_CLIENT, NO_DOSSIER, DATE_COMMANDE, DATE_LIMITE_COMMANDE, PO_CLIENT_COMMANDE, QUANTITE_COMMANDE, EST_UNE_IMPRESSION, TYPE_IMPRESSION, FORMAT_FINAL_IMPRESSION, FORMAT_OUVERT_IMPRESSION, RECTO_VERSO_IMPRESSION, TYPE_ENCRE_RECTO, TYPE_ENCRE_VERSO, TYPE_PAPIER, TYPE_FINITION, NUMEROTAGE_FINITION_DEBUT, NUMEROTAGE_FINITION_FIN, NOTES_FINITION, NOTES_COMMANDE, NO_SOUS_TRAITANT, PO_SOUS_TRAITANT, COUT_COMMANDE, COUT_INFOGRAPHIE, COUT_SOUS_TRAITANT, STATUT_COMMANDE, NOTES_ANNULATION, DATE_MODIFICATION
		from COMMANDE
		where DATE_COMMANDE <= V_DATE_ANNULEE and STATUT_COMMANDE = 'ANNULEE';

	-- Suppression des commandes archivees
	delete from COMMANDE where DATE_COMMANDE <= V_DATE_ANNULEE and STATUT_COMMANDE = 'ANNULEE';
end;
$$; 


-- ===== --
-- INDEX --
-- ===== --


-- Index pour ma recherche trigramme de similarité 
create index IDX_CLIENT_NOM_COMPAGNIE_TRGM on CLIENT using gin (NOM_COMPAGNIE_CLI gin_trgm_ops);
create index IDX_SOUS_TRAITANT_NOM_TRGM on SOUS_TRAITANT using gin (NOM_SOUS_TRAITANT gin_trgm_ops);
create index IDX_TYPE_TRAVAIL on TYPE_TRAVAIL using gin (TYPE_TRAVAIL gin_trgm_ops);


-- ======================= --
-- DONNEES TEST (fictives) --
-- ======================= --


-- Clients
insert into CLIENT (NOM_CONTACT_CLI, PRENOM_CONTACT_CLI, NOM_COMPAGNIE_CLI, ADRESSE_COMPAGNIE_CLI, VILLE_COMPAGNIE_CLI, CODE_POSTAL_COMPAGNIE_CLI, NUMERO_TELEPHONE_COMPAGNIE_CLI)
values 
	('Lavoie', 'Suzanne', 'Restaurant Chez Suzanne', '234, rue Principale', 'Châteauguay', 'J6K 3B2', '4505551234'),
	('Bouchard', 'Marc', 'Garage Bouchard & Fils', '567, boulevard Taschereau', 'Brossard', 'J4W 2T8', '4505555678'),
	('Gagnon', 'Nathalie', 'Centre dentaire Gagnon', '89, avenue Victoria', 'St-Lambert', 'J4P 2J4', '4505559012'),
	('Tremblay', 'Luc', 'Construction Tremblay Inc.', '123, rue Industrielle', 'La Prairie', 'J5R 1K2', '4505553456'),
	(null, 'Luc', 'Hotel repos Inc.', '521, rue du Vide', 'La Prairie', 'J5R 1K9', '4504443456');

-- Types de travail
insert into TYPE_TRAVAIL (TYPE_TRAVAIL)
values 
	('Carte de temps'),
	('Carte d''affaires'),
	('Facture'),
	('Enveloppe'),
	('Dépliant'),
	('Brochure'),
	('Affiche'),
	('Formulaire NCR'),
	('Livret'),
	('Menu'),
	('Calendrier'),
	('Autocollant'),
	('Perforation');

-- Sous-traitants
insert into SOUS_TRAITANT (NOM_SOUS_TRAITANT)
values 
	('Reliure Express'),
	('Découpe Précision'),
	('Laminage Pro'),
	('Dorure & Gaufrage MTL');

-- Commandes
insert into COMMANDE (NO_CLIENT, NO_DOSSIER, DATE_COMMANDE, DATE_LIMITE_COMMANDE, PO_CLIENT_COMMANDE, QUANTITE_COMMANDE, EST_UNE_IMPRESSION, TYPE_IMPRESSION, FORMAT_FINAL_IMPRESSION, FORMAT_OUVERT_IMPRESSION, RECTO_VERSO_IMPRESSION, TYPE_ENCRE_RECTO, TYPE_ENCRE_VERSO, TYPE_PAPIER, TYPE_FINITION, NUMEROTAGE_FINITION_DEBUT, NUMEROTAGE_FINITION_FIN, NOTES_FINITION, NOTES_COMMANDE, NO_SOUS_TRAITANT, PO_SOUS_TRAITANT, COUT_COMMANDE, COUT_INFOGRAPHIE, COUT_SOUS_TRAITANT)
values 
	-- Commande 1: Cartes d'affaires pour Restaurant Chez Suzanne
	(1000, 2, '2024-01-15', '2024-01-22', 'PO-2024-001', 500, true, 'Numérique', '3.5 x 2', null, true, 'CMYK', 'CMYK', 'Carton 14pt', 'Laminé', null, null, 'Laminé mat recto seulement', null, 3, null, 95.00, 25.00, 15.00),
	
	-- Commande 2: Factures NCR pour Garage Bouchard
	(1001, 3, '2024-01-18', '2024-02-01', 'GB-2024-102', 250, true, 'Offset', '8.5 x 11', null, false, 'NB', null, 'NCR 3 copies', 'Broché', 1001, 1250, null, 'Copies: Blanc, Jaune, Rose', 1, 'RE-5521', 325.00, null, 45.00),
	
	-- Commande 3: Dépliants pour Centre dentaire
	(1002, 5, '2024-01-20', '2024-02-05', null, 2000, true, 'Offset', '4 x 9', '8.5 x 11', false, 'CMYK', null, 'Couché 100 lbs', 'Plié', null, null, 'Pli roulé en 3', 'Nouveau design 2024', null, null, 485.00, 75.00, null),
	
	-- Commande 4: Affiches pour Construction Tremblay
	(1003, 7, '2024-01-22', '2024-01-29', 'CT-AFF-01', 50, true, 'Grand format', '24 x 36', null, false, 'CMYK', null, 'Coroplast 4mm', null, null, null, null, 'Pour chantier extérieur', 2, 'DP-1102', 275.00, 50.00, 35.00),
	
	-- commande 5: Perforation pour Hotel repos 
	(1004, 13, '2024-01-24', '2024-02-14', null, 200, false, null, null, null, null, null, null, 'Carton', null, null, null, null, 'Le client va venir chercher sa commande', null, null, 50.00, null, null);

-- Livraisons
insert into LIVRAISON (NO_COMMANDE, NOTES_LIVRAISON, QUANTITE_LIVRAISON, DATE_LIVRAISON, ADRESSE_LIVRAISON, VILLE_LIVRAISON, CODE_POSTAL_LIVRAISON, COUT_LIVRAISON)
values 
	-- Livraison commande 1 (Restaurant)
	(1, 'Livré au comptoir', 500, '2024-01-20', '234, rue Principale', 'Châteauguay', 'J6K 3B2', 0.00),
	
	-- Livraisons commande 2 (Garage - 2 livraisons)
	(2, 'Livraison partielle', 125, '2024-01-25', '567, boulevard Taschereau', 'Brossard', 'J4W 2T8', 15.00),
	(2, 'Livraison finale', 125, '2024-02-01', '567, boulevard Taschereau', 'Brossard', 'J4W 2T8', 15.00),
	
	-- Livraison commande 3 (Centre dentaire)
	(3, null, 2000, '2024-02-03', '89, avenue Victoria', 'St-Lambert', 'J4P 2J4', 20.00),
	
	-- Livraison commande 4 (Construction - sur chantier)
	(4, 'Livrer directement au chantier', 50, '2024-01-28', '450, rue des Érables', 'Candiac', 'J5R 3K9', 35.00);

