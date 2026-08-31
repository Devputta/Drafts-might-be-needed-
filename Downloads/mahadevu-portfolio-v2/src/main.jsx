import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowDownToLine, ArrowRight, Award, BarChart3, BriefcaseBusiness,
  CheckCircle2, ChevronDown, Code2, Database, ExternalLink, Github,
  GraduationCap, Instagram, Linkedin, Mail, Menu, Moon, Search, Send,
  Sparkles, Sun, TestTube2, UserRound, X, Youtube, MapPin, BookOpen,
  BrainCircuit, Layers3, FileText
} from "lucide-react";
import "./styles.css";

const PROFILE = "/profile.png";
const PROFILE_FALLBACK = "/profile-placeholder.png";

const socials = [
  { name: "LinkedIn", handle: "mahadevu-m-p", icon: Linkedin, url: "https://www.linkedin.com/in/mahadevu-m-p-58b51426/" },
  { name: "GitHub", handle: "@Devputta", icon: Github, url: "https://github.com/Devputta" },
  { name: "Email", handle: "mahadevump657@gmail.com", icon: Mail, url: "mailto:mahadevump657@gmail.com" },
  { name: "Instagram", handle: "Add your Instagram", icon: Instagram, url: "#", placeholder: true },
  { name: "YouTube", handle: "Add your YouTube", icon: Youtube, url: "#", placeholder: true }
];

const projects = [
  {
    title: "Manual Testing Project",
    category: "Manual Testing",
    image: "/manual-testing.svg",
    desc: "Manual QA portfolio covering scenarios, detailed test cases, bug reports, regression testing and RTM.",
    brief: "A practical software testing project demonstrating structured QA documentation and testing workflow.",
    topics: ["Test Scenarios", "Test Cases", "Test Data", "Bug Reports", "Regression Testing", "RTM", "STLC", "Negative Testing"],
    tags: ["Manual QA", "Test Cases", "RTM"],
    url: "https://github.com/Devputta/Manual-Testing-Project---1-By-DevPutta"
  },
  {
    title: "AC Company Product Analysis",
    category: "Data Analysis",
    image: "/data-analysis.svg",
    desc: "Data analysis project focused on product and business insights using analytical techniques.",
    brief: "A recruiter-focused analytics project showing how raw business data can be transformed into useful insights.",
    topics: ["Data Cleaning", "EDA", "Business KPIs", "Product Analysis", "Visualization", "Insights"],
    tags: ["Python", "SQL", "Power BI"],
    url: "https://github.com/Devputta/AC-Company-Product-Analysis-"
  },
  {
    title: "AWS + Snowflake + dbt Data Engineering",
    category: "Data Engineering",
    image: "/airbnb.svg",
    desc: "Cloud data pipeline using AWS S3, Snowflake and dbt with layered data architecture.",
    brief: "An end-to-end data engineering project covering ingestion, transformation, incremental processing and analytics-ready datasets.",
    topics: ["AWS S3", "Snowflake", "dbt", "Bronze / Silver / Gold", "Incremental Loading", "SCD Type 2", "Data Quality"],
    tags: ["AWS", "Snowflake", "dbt", "Python"],
    url: "https://github.com/Devputta/DE_PROJECT---AWS---SNOWFLAKE---DBT"
  },
  {
    title: "All-in-One Python & SQL",
    category: "Python & SQL",
    image: "/python-sql.svg",
    desc: "A broad programming repository covering Python fundamentals, advanced concepts, SQL and database practice.",
    brief: "A consolidated learning and practice repository designed to demonstrate breadth across Python and SQL.",
    topics: ["Core Python", "OOP", "Functions", "Collections", "File Handling", "Exceptions", "APIs", "Pandas", "NumPy", "SQL", "Joins", "CTEs", "Subqueries", "Window Functions"],
    tags: ["Python", "SQL", "Pandas", "MySQL"],
    url: "https://github.com/Devputta/ALL-IN-ONE"
  },
  {
    title: "Final Year Machine Learning Project",
    category: "Machine Learning",
    image: "/ml.svg",
    desc: "Machine learning project applying Python-based modeling and data-driven prediction/analysis.",
    brief: "A final-year ML project demonstrating data preparation, model development and evaluation.",
    topics: ["Data Preprocessing", "Feature Work", "Machine Learning", "Model Training", "Evaluation", "Python"],
    tags: ["Python", "ML", "TensorFlow"],
    url: "https://github.com/Devputta/Final-Year-Project"
  },
  {
    title: "Hospital Management System",
    category: "Full Stack",
    image: "/full-stack.svg",
    desc: "Full-stack web application concept for managing hospital-related information and workflows.",
    brief: "A web development project demonstrating application structure, user workflows and database-backed functionality.",
    topics: ["Frontend", "Backend", "Database", "CRUD", "Authentication", "Hospital Workflow"],
    tags: ["Full Stack", "Web", "Database"],
    url: "https://github.com/Devputta/Hospital-Management-System"
  },
  {
    title: "Lumen Cinematic Vault — AI Creation",
    category: "AI & Apps",
    image: "/ai.svg",
    desc: "AI-assisted cinematic website/application project combining creative UI and AI-powered creation.",
    brief: "An AI creation project showing how AI tools can be used to design and build polished web experiences.",
    topics: ["AI-assisted Development", "Prompt Engineering", "Creative UI", "Web App", "AI Tools", "Automation"],
    tags: ["AI", "Web App", "Prompts"],
    url: "https://github.com/Devputta/lumen-cinematic-vault-By-AI"
  }
];

const skillGroups = [
  { title: "Programming", icon: Code2, items: ["Python", "Java", "C", "OOP", "Functions", "Collections", "Exception Handling", "File Handling", "APIs", "Automation"] },
  { title: "Python Ecosystem", icon: Sparkles, items: ["Pandas", "NumPy", "Matplotlib", "Scikit-learn", "TensorFlow", "Keras", "Django", "Jupyter"] },
  { title: "SQL & Databases", icon: Database, items: ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Joins", "CTEs", "Subqueries", "Window Functions", "Aggregations", "Optimization"] },
  { title: "Data Engineering", icon: Layers3, items: ["ETL / ELT", "AWS S3", "Snowflake", "dbt", "Incremental Loading", "SCD Type 2", "Medallion Architecture", "Data Quality"] },
  { title: "Analytics & BI", icon: BarChart3, items: ["Power BI", "DAX", "Power Query", "Excel", "Data Modeling", "KPIs", "Dashboarding", "EDA"] },
  { title: "Manual Testing / QA", icon: TestTube2, items: ["STLC", "Test Scenarios", "Test Cases", "Smoke Testing", "Regression", "Negative Testing", "Bug Reports", "RTM"] },
  { title: "Machine Learning", icon: BrainCircuit, items: ["Data Preprocessing", "Feature Engineering", "Scikit-learn", "TensorFlow", "Keras", "Model Evaluation", "Anomaly Detection"] },
  { title: "AI & App Creation", icon: Sparkles, items: ["Prompt Engineering", "AI APIs", "AI Websites", "Chatbots", "Automation", "Creative UI", "API Integration"] },
  { title: "Tools", icon: FileText, items: ["Git", "GitHub", "VS Code", "Selenium", "UiPath", "Chrome DevTools", "Jupyter"] }
];

const experience = [
  {
    role: "Associate Intern — RPA & Automation",
    company: "Employability.life",
    date: "Nov 2024 – Mar 2025",
    points: ["Worked with UiPath and automation workflows.", "Used Excel and OCR-oriented automation concepts.", "Built practical workflow automation experience."]
  }
];

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("portfolio-theme") || "dark");
  const [menuOpen, setMenuOpen] = useState(false);
  const [active, setActive] = useState("home");
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [photo, setPhoto] = useState(PROFILE_FALLBACK);
  const [showTop, setShowTop] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("portfolio-theme", theme);
  }, [theme]);

  useEffect(() => {
    const ids = ["home", "about", "skills", "projects", "experience", "publication", "education", "contact"];
    const update = () => {
      const point = window.scrollY + 180;
      let current = "home";
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el && el.offsetTop <= point) current = id;
      });
      setActive(current);
      setShowTop(window.scrollY > 700);
    };
    window.addEventListener("scroll", update, { passive: true });
    update();

    const observer = new IntersectionObserver(
      entries => entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add("visible");
      }),
      { threshold: 0.12 }
    );
    document.querySelectorAll(".reveal").forEach(el => observer.observe(el));

    return () => {
      window.removeEventListener("scroll", update);
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = selected ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [selected]);

  const categories = useMemo(() => ["All", ...new Set(projects.map(p => p.category))], []);

  const visibleProjects = projects.filter(project => {
    const categoryMatch = filter === "All" || project.category === filter;
    const text = `${project.title} ${project.category} ${project.desc} ${project.tags.join(" ")}`.toLowerCase();
    return categoryMatch && text.includes(search.toLowerCase());
  });

  const go = id => {
    setMenuOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="site">
      <div className="noise" />
      <header className="nav">
        <button className="brand" onClick={() => go("home")}>it&apos;s <i>me</i></button>

        <nav className={menuOpen ? "nav-links open" : "nav-links"}>
          {[
            ["home", "Home"], ["about", "About"], ["skills", "Skills"],
            ["projects", "Projects"], ["experience", "Experience"],
            ["publication", "Publication"], ["education", "Education"], ["contact", "Contact"]
          ].map(([id, label]) => (
            <button key={id} className={active === id ? "active" : ""} onClick={() => go(id)}>
              {label}
            </button>
          ))}
        </nav>

        <div className="nav-actions">
          <button className="icon-btn" title="Toggle theme" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          </button>
          <button className="mobile-menu" onClick={() => setMenuOpen(v => !v)} aria-label="Open menu">
            {menuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </header>

      <main>
        <section id="home" className="hero wrap">
          <div className="hero-copy reveal">
            <span className="eyebrow">SOFTWARE ENGINEER · DATA · QA · AI</span>
            <h1>Building useful things<br /><em>with data &amp; code.</em></h1>
            <p className="hero-text">
              I&apos;m Mahadevu M P. I build practical software, analytics and data solutions across Python,
              SQL, Data Engineering, Power BI, Manual Testing, Machine Learning and AI-powered applications.
            </p>
            <div className="hero-actions">
              <a className="btn light" href="/resume.pdf" download>
                <ArrowDownToLine size={15} /> Download Resume
              </a>
              <button className="btn dark" onClick={() => go("projects")}>
                Explore Projects <ArrowRight size={15} />
              </button>
            </div>
            <div className="social-strip">
              {socials.slice(0, 3).map(item => {
                const Icon = item.icon;
                return (
                  <a href={item.url} target={item.url.startsWith("http") ? "_blank" : undefined} rel="noreferrer" key={item.name}>
                    <Icon size={15} /> {item.name}
                  </a>
                );
              })}
            </div>
          </div>

          <div className="hero-profile reveal">
            <div className="photo-frame">
              <img src={photo} alt="Mahadevu M P profile" onError={() => setPhoto(PROFILE_FALLBACK)} />
            </div>
            
          </div>
        </section>

        <section className="intro-band">
          <div className="wrap band-grid">
            <span>PYTHON</span><span>SQL</span><span>DATA ENGINEERING</span><span>POWER BI</span>
            <span>MANUAL TESTING</span><span>MACHINE LEARNING</span><span>AI APPS</span>
          </div>
        </section>

        <section id="about" className="section wrap reveal">
          <SectionTitle index="01" title="About me" icon={UserRound} />
          <div className="about-grid">
            <div>
              <p className="large-copy">
                I&apos;m interested in the complete software lifecycle — from writing Python and SQL,
                to building data pipelines, dashboards, test cases, ML models and AI-assisted web applications.
              </p>
              <p className="muted">
                This portfolio is intentionally broad so recruiters can quickly see both my core strengths
                and the range of projects I have worked on.
              </p>
            </div>
            <div className="fact-list">
              <Fact label="FOCUS" value="Software Engineering + Data" />
              <Fact label="PRIMARY STACK" value="Python · SQL · AWS · Snowflake · dbt" />
              <Fact label="QA" value="Manual Testing · Selenium · RTM" />
              <Fact label="AI" value="AI Apps · Prompt Engineering · Automation" />
              <Fact label="EMAIL" value="mahadevump657@gmail.com" />
            </div>
          </div>
        </section>

        <section id="skills" className="section wrap reveal">
          <SectionTitle index="02" title="Skills" icon={Sparkles} />
          <p className="muted section-lead">The complete skill map — including Python, SQL, data engineering, analytics, QA, ML and AI.</p>
          <div className="skills-grid">
            {skillGroups.map(group => {
              const Icon = group.icon;
              return (
                <div className="skill-card" key={group.title}>
                  <div className="skill-head"><Icon size={18} /><h3>{group.title}</h3></div>
                  <div className="pills">{group.items.map(item => <span key={item}>{item}</span>)}</div>
                </div>
              );
            })}
          </div>
        </section>

        <section id="projects" className="section wrap reveal">
          <div className="title-row">
            <SectionTitle index="03" title="Projects" icon={BarChart3} />
            <a className="outline-btn" href="https://github.com/Devputta" target="_blank" rel="noreferrer">
              <Github size={14} /> View GitHub
            </a>
          </div>

          <div className="project-tools">
            <div className="filters">
              {categories.map(category => (
                <button key={category} className={filter === category ? "selected" : ""} onClick={() => setFilter(category)}>
                  {category}
                </button>
              ))}
            </div>
            <label className="search-box">
              <Search size={14} />
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search projects" />
            </label>
          </div>

          <div className="project-grid">
            {visibleProjects.map(project => (
              <article className="project-card" key={project.title} onClick={() => setSelected(project)} tabIndex="0"
                onKeyDown={e => e.key === "Enter" && setSelected(project)}>
                <div className="project-image">
                  <img src={project.image} alt="" />
                  <span>{project.category}</span>
                  <b>OPEN <ArrowRight size={12} /></b>
                </div>
                <div className="project-body">
                  <h3>{project.title}</h3>
                  <p>{project.desc}</p>
                  <div className="tags">{project.tags.map(tag => <span key={tag}>{tag}</span>)}</div>
                  <button className="project-link">View brief <ArrowRight size={13} /></button>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section id="experience" className="section wrap reveal">
          <SectionTitle index="04" title="Experience" icon={BriefcaseBusiness} />
          <div className="timeline">
            {experience.map(item => (
              <div className="timeline-item" key={item.role}>
                <div className="timeline-dot" />
                <div>
                  <h3>{item.role}</h3>
                  <div className="timeline-meta">{item.company} · {item.date}</div>
                  <ul>{item.points.map(point => <li key={point}>{point}</li>)}</ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section id="publication" className="section wrap reveal">
          <SectionTitle index="05" title="Publication" icon={BookOpen} />
          <a className="publication-card" href="https://tarce.co/index.php/tarce/article/view/4261" target="_blank" rel="noreferrer">
            <div className="pub-icon"><BookOpen size={22} /></div>
            <div className="pub-content">
              <span>RESEARCH / PUBLICATION</span>
              <h3>Published Research Article</h3>
              <p>View the published article on the TARCE platform.</p>
              <b>Open publication <ExternalLink size={13} /></b>
            </div>
            <ArrowRight className="pub-arrow" size={20} />
          </a>
        </section>

        <section id="education" className="section wrap reveal">
          <SectionTitle index="06" title="Education & certifications" icon={GraduationCap} />
          <div className="education-grid">
            <div className="education-card">
              <GraduationCap size={20} />
              <h3>BE — Information Science &amp; Engineering</h3>
              <p>PES College of Engineering, Mandya</p>
              <small>2021 – 2025</small>
            </div>
            <div className="education-card">
              <GraduationCap size={20} />
              <h3>Diploma — Computer Science</h3>
              <p>Government Polytechnic, Ramanagara</p>
              <small>2018 – 2021</small>
            </div>
            <div className="education-card">
              <Award size={20} />
              <h3>Certifications &amp; Learning</h3>
              <p>Python · SQL · IoT · Cloud · Cyber Security · Testing · Data &amp; AI</p>
              <small>Continuous learning</small>
            </div>
          </div>
        </section>

        <section id="contact" className="section wrap reveal">
          <SectionTitle index="07" title="Get in touch" icon={Mail} />
          <p className="section-lead muted">Have questions or ready to collaborate on data, software, QA or engineering projects? Drop a message — I&apos;ll get back to you.</p>

          <div className="contact-grid">
            <div className="contact-links">
              <ContactCard icon={Mail} title="Email us" value="mahadevump657@gmail.com" href="mailto:mahadevump657@gmail.com" />
              <ContactCard icon={Linkedin} title="LinkedIn" value="mahadevu-m-p" href="https://www.linkedin.com/in/mahadevu-m-p-58b51426/" />
              <ContactCard icon={Github} title="GitHub" value="@Devputta" href="https://github.com/Devputta" />
              <ContactCard icon={MapPin} title="Location" value="Bengaluru, Karnataka" href="https://www.google.com/maps/search/?api=1&query=Bengaluru%2C%20Karnataka" />
            </div>

            <div className="contact-form">
              <div className="form-field"><input id="name" placeholder="Name" /></div>
              <div className="form-field"><input id="email" type="email" placeholder="Email" /></div>
              <div className="form-field"><textarea id="message" placeholder="Message" rows="7" /></div>
              <button className="submit-btn" onClick={() => {
                const name = document.getElementById("name").value.trim();
                const email = document.getElementById("email").value.trim();
                const message = document.getElementById("message").value.trim();
                if (!name || !email || !message) {
                  alert("Please fill Name, Email and Message.");
                  return;
                }
                const subject = encodeURIComponent(`Portfolio enquiry from ${name}`);
                const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\n${message}`);
                window.location.href = `mailto:mahadevump657@gmail.com?subject=${subject}&body=${body}`;
              }}>
                Submit <Send size={14} />
              </button>
              <small className="form-note">This form opens your email app. No phone number is displayed.</small>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer wrap">
        <span>© 2026 Mahadevu M P</span>
        <span>SOFTWARE · DATA · QA · ML · AI</span>
        <button onClick={() => go("home")}>Back to top ↑</button>
      </footer>

      {showTop && <button className="floating-top" onClick={() => go("home")}>↑</button>}

      {selected && (
        <div className="modal-overlay" onMouseDown={e => e.target === e.currentTarget && setSelected(null)}>
          <div className="modal">
            <button className="modal-close" onClick={() => setSelected(null)}><X size={18} /></button>
            <div className="modal-image"><img src={selected.image} alt={selected.title} /></div>
            <div className="modal-content">
              <span className="modal-category">{selected.category}</span>
              <h2>{selected.title}</h2>
              <p>{selected.brief}</p>
              <h4>TOPICS COVERED</h4>
              <div className="topic-list">
                {selected.topics.map(topic => <div key={topic}><CheckCircle2 size={14} /> {topic}</div>)}
              </div>
              <div className="tags">{selected.tags.map(tag => <span key={tag}>{tag}</span>)}</div>
              <div className="modal-actions">
                <a className="btn light" href={selected.url} target="_blank" rel="noreferrer">
                  <Github size={15} /> Open GitHub <ExternalLink size={12} />
                </a>
                <button className="btn dark" onClick={() => setSelected(null)}>Close</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SectionTitle({ index, title, icon: Icon }) {
  return (
    <div className="section-title">
      <Icon size={19} />
      <div>
        <small>{index} / SECTION</small>
        <h2>{title}</h2>
      </div>
    </div>
  );
}

function Fact({ label, value }) {
  return <div className="fact"><small>{label}</small><strong>{value}</strong></div>;
}

function ContactCard({ icon: Icon, title, value, href }) {
  return (
    <a className="contact-card" href={href} target={href.startsWith("http") ? "_blank" : undefined} rel="noreferrer">
      <span className="contact-icon"><Icon size={19} /></span>
      <span><b>{title}</b><small>{value}</small></span>
      <span className="round-arrow">↗</span>
    </a>
  );
}

createRoot(document.getElementById("root")).render(<App />);
