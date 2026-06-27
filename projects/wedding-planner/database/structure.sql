CREATE TABLE mariages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_code TEXT NOT NULL,
    date_evenement TEXT NOT NULL,
    budget_max REAL NOT NULL,
    ville_residence TEXT NOT NULL,
    lieu_id INTEGER,
    FOREIGN KEY (lieu_id) REFERENCES lieux(id)
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meal_name, category)
);

CREATE TABLE menus_traiteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    nom_plat TEXT,
    categorie TEXT,
    cout_unitaire REAL,
    --source TEXT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE budget_depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    categorie TEXT NOT NULL, -- Ex: 'Traiteur', 'Animation', 'Logistique'
    intitule TEXT NOT NULL,  -- Ex: 'Buffet Gourmet', 'Location Photobooth'
    montant_estime REAL NOT NULL,
    montant_propose REAL,
    montant_paye REAL DEFAULT 0.0,
    statut TEXT CHECK (statut IN ('Prevu', 'Acompte_Paye', 'Solde_Paye', 'En_Attente_Validation')) DEFAULT 'Prevu',
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);

CREATE TABLE playlist_didier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    titre TEXT NOT NULL,
    artiste TEXT NOT NULL,
    genre TEXT,
    moment_diffusion TEXT CHECK (moment_diffusion IN ('Cocktail', 'Diner', 'Soiree')),
    statut_validation TEXT DEFAULT 'Valide' CHECK (statut_validation IN ('Valide', 'Blackliste')),
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE,
    UNIQUE(mariage_id, titre, artiste)
);

CREATE TABLE taches_planning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    titre TEXT NOT NULL,
    description TEXT,
    date_limite TEXT NOT NULL,
    statut TEXT CHECK (statut IN ('A_Faire', 'En_Cours', 'Termine', 'Annule')),
    priorite Text DEFAULT 'Moyenne' CHECK (priorite IN ('Haute', 'Moyenne', 'Basse')),
    responsable_agent TEXT CHECK (responsable_agent IN ('Lieux', 'Budget', 'Planning', 'Traiteur', 'Invite', 'Didier', 'Flight', 'Humain')),
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);

CREATE TABLE invites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE,
    statut_rsvp TEXT CHECK (statut_rsvp IN ('En_Attente', 'Confirme', 'Decline')) DEFAULT 'En_Attente',
    besoin_vol INTEGER DEFAULT 0,
    ville_origine TEXT,
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);

CREATE TABLE offres_vols_disponibles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mariage_id INTEGER,
    ville_depart VARCHAR(100) NOT NULL,
    compagnie VARCHAR(100) NOT NULL,
    prix_estime DECIMAL(10,2) NOT NULL,
    duree_vol VARCHAR(50) NOT NULL,
    --nombre_escale INTEGER
    FOREIGN KEY (mariage_id) REFERENCES mariages(id) ON DELETE CASCADE
);