import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

import congoLogo from "../../assets/images/logo/congo-logo.png";

import "../../Styles/ClientDashboard.css";


function ClientDashboard() {
  const {
    user,
    logout,
  } = useAuth();


  const handleLogout = async () => {
    await logout();
  };


  return (
    <div className="client-dashboard">

      {/* =========================
          SIDEBAR
      ========================= */}

      <aside className="client-sidebar">

        <Link
          to="/"
          className="client-logo"
        >
          <img
            src={congoLogo}
            alt="Artisans du Congo"
          />
        </Link>


        <nav className="client-menu">

          <Link
            to="/client"
            className="client-menu-link active"
          >
            <span>⌂</span>
            Tableau de bord
          </Link>


          <Link
            to="/artisans"
            className="client-menu-link"
          >
            <span>⌕</span>
            Trouver un artisan
          </Link>


          <Link
            to="/client/demandes"
            className="client-menu-link"
          >
            <span>▤</span>
            Mes demandes
          </Link>


          <Link
            to="/client/propositions"
            className="client-menu-link"
          >
            <span>◫</span>
            Propositions
          </Link>


          <Link
            to="/client/messages"
            className="client-menu-link"
          >
            <span>✉</span>
            Messages
          </Link>


          <Link
            to="/client/favoris"
            className="client-menu-link"
          >
            <span>♡</span>
            Favoris
          </Link>

        </nav>


        <div className="client-sidebar-bottom">

          <Link
            to="/client/profil"
            className="client-menu-link"
          >
            <span>⚙</span>
            Mon profil
          </Link>


          <button
            type="button"
            className="client-logout"
            onClick={handleLogout}
          >
            <span>↪</span>
            Se déconnecter
          </button>

        </div>

      </aside>


      {/* =========================
          CONTENT
      ========================= */}

      <div className="client-main">

        {/* HEADER */}

        <header className="client-topbar">

          <div>
            <p className="client-location">
              🇨🇬 République du Congo
            </p>
          </div>


          <div className="client-topbar-actions">

            <button
              type="button"
              className="notification-button"
            >
              🔔
              <span>2</span>
            </button>


            <div className="client-user">

              <div className="client-avatar">
                {user?.first_name
                  ?.charAt(0)
                  ?.toUpperCase() || "U"}
              </div>


              <div className="client-user-info">
                <strong>
                  {user?.first_name || "Utilisateur"}
                </strong>

                <span>
                  Client
                </span>
              </div>

            </div>

          </div>

        </header>


        {/* PAGE */}

        <main className="client-content">

          {/* WELCOME */}

          <section className="client-welcome">

            <div>

              <span className="client-welcome-label">
                ESPACE CLIENT
              </span>

              <h1>
                Bonjour{" "}
                {user?.first_name || "👋"}
                <span> 👋</span>
              </h1>

              <p>
                Quel projet souhaitez-vous
                réaliser aujourd'hui ?
              </p>

            </div>


            <Link
              to="/demandes/nouvelle"
              className="new-request-button"
            >
              <span>+</span>
              Faire une demande
            </Link>

          </section>


          {/* SEARCH */}

          <section className="client-search-card">

            <div className="client-search-title">
              <span>⌕</span>

              <div>
                <strong>
                  Trouvez le bon artisan
                </strong>

                <p>
                  Recherchez un professionnel
                  selon votre besoin.
                </p>
              </div>
            </div>


            <div className="client-search-form">

              <div className="client-search-input">
                <span>⌕</span>

                <input
                  type="text"
                  placeholder={
                    "Plombier, électricien, maçon..."
                  }
                />
              </div>


              <div className="client-search-input location">
                <span>📍</span>

                <input
                  type="text"
                  placeholder="Brazzaville"
                />
              </div>


              <button type="button">
                Rechercher
              </button>

            </div>

          </section>


          {/* STATISTICS */}

          <section className="client-stats">

            <article className="client-stat-card">

              <div className="stat-icon green">
                ▤
              </div>

              <div>
                <span>
                  Demandes actives
                </span>

                <strong>3</strong>
              </div>

            </article>


            <article className="client-stat-card">

              <div className="stat-icon yellow">
                ◫
              </div>

              <div>
                <span>
                  Propositions reçues
                </span>

                <strong>5</strong>
              </div>

            </article>


            <article className="client-stat-card">

              <div className="stat-icon red">
                ✉
              </div>

              <div>
                <span>
                  Nouveaux messages
                </span>

                <strong>2</strong>
              </div>

            </article>


            <article className="client-stat-card">

              <div className="stat-icon dark">
                ★
              </div>

              <div>
                <span>
                  Projets terminés
                </span>

                <strong>8</strong>
              </div>

            </article>

          </section>


          {/* DASHBOARD GRID */}

          <section className="client-dashboard-grid">

            {/* REQUESTS */}

            <div className="dashboard-panel requests-panel">

              <div className="panel-header">

                <div>
                  <span className="panel-label">
                    MES PROJETS
                  </span>

                  <h2>
                    Demandes récentes
                  </h2>
                </div>


                <Link to="/client/demandes">
                  Voir tout →
                </Link>

              </div>


              <div className="request-list">

                <article className="request-item">

                  <div className="request-icon">
                    🔧
                  </div>

                  <div className="request-information">

                    <strong>
                      Réparation fuite d'eau
                    </strong>

                    <span>
                      Plomberie • Brazzaville
                    </span>

                  </div>

                  <span className="request-status progress">
                    EN COURS
                  </span>

                </article>


                <article className="request-item">

                  <div className="request-icon">
                    🎨
                  </div>

                  <div className="request-information">

                    <strong>
                      Peinture du salon
                    </strong>

                    <span>
                      Peinture • Brazzaville
                    </span>

                  </div>

                  <span className="request-status published">
                    PUBLIÉE
                  </span>

                </article>


                <article className="request-item">

                  <div className="request-icon">
                    ⚡
                  </div>

                  <div className="request-information">

                    <strong>
                      Installation électrique
                    </strong>

                    <span>
                      Électricité • Bacongo
                    </span>

                  </div>

                  <span className="request-status waiting">
                    EN ATTENTE
                  </span>

                </article>

              </div>

            </div>


            {/* ACTIVITY */}

            <div className="dashboard-panel activity-panel">

              <div className="panel-header">

                <div>
                  <span className="panel-label">
                    ACTIVITÉ
                  </span>

                  <h2>
                    Dernières nouvelles
                  </h2>
                </div>

              </div>


              <div className="activity-list">

                <div className="activity-item">

                  <div className="activity-icon">
                    ◫
                  </div>

                  <div>
                    <strong>
                      Nouvelle proposition
                    </strong>

                    <p>
                      Un artisan a répondu à
                      votre demande de plomberie.
                    </p>

                    <span>
                      Il y a 15 min
                    </span>
                  </div>

                </div>


                <div className="activity-item">

                  <div className="activity-icon">
                    ✉
                  </div>

                  <div>
                    <strong>
                      Nouveau message
                    </strong>

                    <p>
                      Vous avez reçu un nouveau
                      message d'un artisan.
                    </p>

                    <span>
                      Il y a 1 h
                    </span>
                  </div>

                </div>


                <div className="activity-item">

                  <div className="activity-icon">
                    ✓
                  </div>

                  <div>
                    <strong>
                      Projet terminé
                    </strong>

                    <p>
                      Vous pouvez maintenant
                      laisser un avis.
                    </p>

                    <span>
                      Hier
                    </span>
                  </div>

                </div>

              </div>

            </div>

          </section>


          {/* BOTTOM CTA */}

          <section className="client-bottom-cta">

            <div>

              <span>
                🇨🇬 ARTISANS DU CONGO
              </span>

              <h2>
                Un projet en tête ?
              </h2>

              <p>
                Publiez gratuitement votre demande
                et recevez des propositions
                d'artisans.
              </p>

            </div>


            <Link
              to="/demandes/nouvelle"
              className="bottom-cta-button"
            >
              Publier mon projet →
            </Link>

          </section>

        </main>

      </div>

    </div>
  );
}


export default ClientDashboard;
