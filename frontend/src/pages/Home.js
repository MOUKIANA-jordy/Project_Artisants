import { Link } from "react-router-dom";
import "../Styles/Home.css";

import maconnerieImg from "../assets/images/metiers/maconnerie.jpg";
import electriciteImg from "../assets/images/metiers/electricite.jpg";
import plomberieImg from "../assets/images/metiers/plomberie.jpg";
import menuiserieImg from "../assets/images/metiers/menuiserie.jpg";
import peintureImg from "../assets/images/metiers/peinture.jpg";
import mecaniqueImg from "../assets/images/metiers/mecanique.jpg";
import nettoyageImg from "../assets/images/metiers/nettoyage.jpg";
import jardinageImg from "../assets/images/metiers/jardinage.jpg";
import congoLogo from "../assets/images/logo/congo-logo.png";

const popularCategories = [
  {
    name: "Maçonnerie",
    icon: "🧱",
    image: maconnerieImg,
  },
  {
    name: "Électricité",
    icon: "⚡",
    image: electriciteImg,
  },
  {
    name: "Plomberie",
    icon: "🔧",
    image: plomberieImg,
  },
  {
    name: "Menuiserie",
    icon: "🪚",
    image: menuiserieImg,
  },
  {
    name: "Peinture",
    icon: "🎨",
    image: peintureImg,
  },
  {
    name: "Mécanique",
    icon: "⚙️",
    image: mecaniqueImg,
  },
  {
    name: "Nettoyage",
    icon: "🧹",
    image: nettoyageImg,
  },
  {
    name: "Jardinage",
    icon: "🌿",
    image: jardinageImg,
  },
];

function Home() {
  return (
    <div className="home-page">
      {/* ================= HEADER ================= */}

      <header className="home-header">
        <Link to="/" className="brand brand-logo" aria-label="Artisans du Congo - Accueil">
  	 <img
    	  src={congoLogo}
    	  alt="Artisans du Congo"
    	  className="brand-logo-image"
  				/>
	</Link>

        <nav className="home-navigation">
          <Link to="/" className="active">
            Accueil
          </Link>

          <Link to="/artisans">
            Artisans
          </Link>

          <Link to="/demandes">
            Demandes
          </Link>

          <a href="#categories">
            Métiers
          </a>

          <a href="#how-it-works">
            Comment ça marche
          </a>

          <a href="#about">
            À propos
          </a>
        </nav>

        <div className="header-actions">
          <Link
            to="/login"
            className="login-button"
          >
            Se connecter
          </Link>

          <Link
            to="/register"
            className="register-button"
          >
            S'inscrire
          </Link>
        </div>
      </header>

      {/* ================= HERO ================= */}

      <main>
        <section className="hero">
          <div className="hero-overlay" />

          <div className="hero-content">
            <p className="hero-label">
              🇨🇬 Le savoir-faire congolais
            </p>

            <h1>
              Le Congo
              <br />
              se construit
              <br />
              <span>de nos mains</span>
            </h1>

            <p className="hero-description">
              Trouvez un artisan de confiance
              <br />
              et donnez vie à vos projets.
            </p>

            {/* Recherche */}

            <form
              className="hero-search"
              onSubmit={(event) =>
                event.preventDefault()
              }
            >
              <div className="search-field">
                <span>⌕</span>

                <input
                  type="text"
                  placeholder="Quel service recherchez-vous ?"
                  aria-label="Service recherché"
                />
              </div>

              <div className="search-location">
                <span>📍</span>

                <input
                  type="text"
                  placeholder="Brazzaville"
                  aria-label="Localisation"
                />
              </div>

              <button type="submit">
                Rechercher
              </button>
            </form>

            {/* Avantages */}

            <div className="hero-features">
              <div className="hero-feature">
                <div className="feature-icon">
                  ✓
                </div>

                <div>
                  <strong>
                    Artisans vérifiés
                  </strong>

                  <span>
                    et qualifiés
                  </span>
                </div>
              </div>

              <div className="hero-feature">
                <div className="feature-icon">
                  ★
                </div>

                <div>
                  <strong>
                    Avis clients
                  </strong>

                  <span>
                    réels
                  </span>
                </div>
              </div>

              <div className="hero-feature">
                <div className="feature-icon">
                  🇨🇬
                </div>

                <div>
                  <strong>
                    Partout au Congo
                  </strong>

                  <span>
                    Trouvez près de vous
                  </span>
                </div>
              </div>

              <div className="hero-feature">
                <div className="feature-icon">
                  🛡
                </div>

                <div>
                  <strong>
                    Service sécurisé
                  </strong>

                  <span>
                    Mise en relation fiable
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ================= CATEGORIES ================= */}

        <section
          className="categories-section"
          id="categories"
        >
          <div className="section-heading">
            <div>
              <span className="section-label">
                NOS SERVICES
              </span>

              <h2>
                Trouvez le bon artisan
              </h2>

              <p>
                Découvrez les professionnels
                disponibles selon votre besoin.
              </p>
            </div>

            <Link
              to="/categories"
              className="view-all"
            >
              Voir tous les métiers →
            </Link>
          </div>

          <div className="categories-grid">
            {popularCategories.map(
              (category) => (
                <Link
                  to={`/artisans?metier=${encodeURIComponent(
                    category.name
                  )}`}
                  className="category-card"
                  key={category.name}
                >
                  <div className="category-image">
  			<img
    			src={category.image}
    			alt={`Artisan - ${category.name}`}
    			loading="lazy"
  				/>
			</div>

                  <div className="category-info">
                    <span className="category-icon">
                      {category.icon}
                    </span>

                    <strong>
                      {category.name}
                    </strong>
                  </div>
                </Link>
              )
            )}
          </div>
        </section>

        {/* ================= CTA ================= */}

        <section
          className="home-cta"
          id="how-it-works"
        >
          <div className="cta-content">
            <span className="section-label">
              BESOIN D'UN PROFESSIONNEL ?
            </span>

            <h2>
              Votre projet commence ici.
            </h2>

            <p>
              Décrivez votre besoin et recevez
              des propositions d'artisans.
            </p>

            <Link
              to="/demandes/nouvelle"
              className="cta-button"
            >
              Faire une demande →
            </Link>
          </div>

          <div className="steps">
            <div className="step">
              <span>1</span>

              <div>
                <strong>
                  Décrivez votre projet
                </strong>

                <p>
                  Expliquez simplement ce dont
                  vous avez besoin.
                </p>
              </div>
            </div>

            <div className="step">
              <span>2</span>

              <div>
                <strong>
                  Recevez des propositions
                </strong>

                <p>
                  Des artisans intéressés
                  répondent à votre demande.
                </p>
              </div>
            </div>

            <div className="step">
              <span>3</span>

              <div>
                <strong>
                  Choisissez votre artisan
                </strong>

                <p>
                  Consultez son profil et les
                  avis avant de décider.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ================= ARTISAN CTA ================= */}

        <section
          className="artisan-cta"
          id="about"
        >
          <div>
            <span className="section-label">
              VOUS ÊTES ARTISAN ?
            </span>

            <h2>
              Votre savoir-faire mérite
              d'être visible.
            </h2>

            <p>
              Présentez votre activité,
              développez votre réputation et
              trouvez de nouveaux clients.
            </p>
          </div>

          <Link
            to="/register"
            className="artisan-button"
          >
            Rejoindre les artisans →
          </Link>
        </section>
      </main>

      {/* ================= FOOTER ================= */}

      <footer className="home-footer">
        <div>
          <strong>
            ARTISANS DU CONGO
          </strong>

          <p>
            Le savoir-faire congolais,
            à portée de main.
          </p>
        </div>

        <p>
          © 2026 Artisans du Congo
        </p>
      </footer>
    </div>
  );
}

export default Home;
