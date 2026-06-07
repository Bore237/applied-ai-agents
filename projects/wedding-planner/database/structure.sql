CREATE TABLE mariages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_code TEXT NOT NULL,
    date_evenement TEXT NOT NULL,
    budget_max REAL NOT NULL,
    ville_depart_invites TEXT DEFAULT 'Paris'
);

CREATE TABLE lieux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    ville TEXT NOT NULL,
    capacite_max INTEGER NOT NULL,
    tarif_location REAL NOT NULL,
    style TEXT,
    disponible INTEGER DEFAULT 1
);

CREATE TABLE menus_prix (
    meal_id TEXT PRIMARY KEY,
    meal_name TEXT NOT NULL,
    category TEXT NOT NULL,
    prix_unitaire REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menus_traiteur (
    id INTEGER PRIMARY KEY,
    mariage_id INTEGER,
    nom_plat TEXT,
    categorie TEXT,
    cout_unitaire REAL,
    source TEXT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE budget_depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    categorie TEXT NOT NULL,
    intitule TEXT NOT NULL,
    montant_estime REAL NOT NULL,
    montant_paye REAL DEFAULT 0.0,
    statut TEXT CHECK (statut IN ('Prevu', 'Acompte_Paye', 'Solde_Paye')),
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);

CREATE TABLE invites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT,
    statut_rsvp TEXT CHECK (statut_rsvp IN ('En_Attente', 'Confirme', 'Decline')),
    regime_alimentaire TEXT DEFAULT 'Aucun',
    besoin_vol INTEGER DEFAULT 0,
    ville_origine TEXT,
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);

CREATE TABLE playlist_didier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    titre TEXT NOT NULL,
    artiste TEXT NOT NULL,
    genre TEXT,
    moment_diffusion TEXT CHECK (moment_diffusion IN ('Cocktail', 'Diner', 'Soiree')),
    statut_validation TEXT DEFAULT 'Valide'
        CHECK (statut_validation IN ('Valide', 'Blackliste')),
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);

CREATE TABLE taches_planning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    titre TEXT NOT NULL,
    description TEXT,
    date_limite TEXT NOT NULL,
    statut TEXT CHECK (statut IN ('A_Faire', 'En_Cours', 'Termine')),
    responsable_agent TEXT,
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);