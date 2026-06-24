-- =============================================================
-- Seed: Skills Taxonomy — 5 Domains, 22 Categories, 300+ Skills
-- Dependencies: 000_skills_complete_ddl.sql (run first)
-- Usage: psql -f seed_skills_taxonomy.sql
-- =============================================================

BEGIN;

-- =============================================================
-- DOMAIN 1: Software Engineering (top category id: SE_ROOT)
-- =============================================================

-- Root category
INSERT INTO skill_categories (category_id, name, slug, description, level, sort_order) VALUES
    ('se_root', 'Software Engineering', 'software-engineering', 'Core software engineering skills including system design, architecture, and engineering best practices', 0, 1)
ON CONFLICT (name) DO NOTHING;

-- Sub-categories
INSERT INTO skill_categories (category_id, parent_category_id, name, slug, description, level, sort_order) VALUES
    ('se_lang',  'se_root', 'Programming Languages', 'programming-languages', 'General-purpose and domain-specific programming languages', 1, 1),
    ('se_web',   'se_root', 'Web Development', 'web-development', 'Frontend and backend web frameworks and tools', 1, 2),
    ('se_devops','se_root', 'DevOps & Infrastructure', 'devops-infrastructure', 'CI/CD, cloud platforms, containerization, and IaC', 1, 3),
    ('se_db',    'se_root', 'Databases & Storage', 'databases-storage', 'Relational, NoSQL, caching, and data storage', 1, 4),
    ('se_arch',  'se_root', 'System Design & Architecture', 'system-design-architecture', 'Distributed systems, microservices, and software architecture', 1, 5)
ON CONFLICT (name) DO NOTHING;

-- Programming Languages skills
INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    -- Python
    ('sk_py',   'se_lang', 'Python', 'python', 'High-level interpreted language for web, data, and automation', 5, ARRAY['python3', 'cpython'], '{"icon":"python","color":"#3776AB","tags":["backend","data","automation"]}'),
    ('sk_js',   'se_lang', 'JavaScript', 'javascript', 'Dynamic language powering web browsers and Node.js', 5, ARRAY['js', 'es6', 'ecmascript'], '{"icon":"javascript","color":"#F7DF1E","tags":["frontend","backend"]}'),
    ('sk_ts',   'se_lang', 'TypeScript', 'typescript', 'Typed superset of JavaScript for large-scale applications', 5, ARRAY['ts', 'typescript'], '{"icon":"typescript","color":"#3178C6","tags":["frontend","backend","type-safe"]}'),
    ('sk_go',   'se_lang', 'Go', 'go', 'Statically typed compiled language by Google for backend systems', 5, ARRAY['golang'], '{"icon":"go","color":"#00ADD8","tags":["backend","systems"]}'),
    ('sk_rust', 'se_lang', 'Rust', 'rust', 'Systems language focussing on safety, speed, and concurrency', 5, ARRAY['rust-lang'], '{"icon":"rust","color":"#000000","tags":["systems","embedded"]}'),
    ('sk_java', 'se_lang', 'Java', 'java', 'Object-oriented language for enterprise and Android', 5, ARRAY['java-11', 'java-17'], '{"icon":"java","color":"#ED8B00","tags":["backend","enterprise"]}'),
    ('sk_cpp',  'se_lang', 'C++', 'cpp', 'Systems language for performance-critical applications', 5, ARRAY['c-plus-plus', 'cpp'], '{"icon":"cpp","color":"#00599C","tags":["systems","game-dev"]}'),
    ('sk_cs',   'se_lang', 'C#', 'csharp', 'Microsoft .NET language for enterprise and game development', 5, ARRAY['c-sharp', 'dotnet'], '{"icon":"csharp","color":"#239120","tags":["backend","game-dev","windows"]}'),
    ('sk_kotlin','se_lang', 'Kotlin', 'kotlin', 'Modern JVM language for Android and backend', 5, ARRAY['kotlin-lang'], '{"icon":"kotlin","color":"#7F52FF","tags":["android","backend"]}'),
    ('sk_swift','se_lang', 'Swift', 'swift', 'Apple language for iOS, macOS, and server-side', 5, ARRAY['swift-lang'], '{"icon":"swift","color":"#F05138","tags":["ios","macos"]}'),
    ('sk_ruby', 'se_lang', 'Ruby', 'ruby', 'Dynamic language known for Rails web framework', 5, ARRAY['ruby-lang'], '{"icon":"ruby","color":"#CC342D","tags":["backend","web"]}'),
    ('sk_php',  'se_lang', 'PHP', 'php', 'Server-side scripting language for web applications', 5, ARRAY['php-lang'], '{"icon":"php","color":"#777BB4","tags":["backend","web"]}'),
    ('sk_scala','se_lang', 'Scala', 'scala', 'Functional JVM language for data-intensive applications', 5, ARRAY['scala-lang'], '{"icon":"scala","color":"#DC322F","tags":["backend","big-data"]}'),
    ('sk_elixir','se_lang', 'Elixir', 'elixir', 'Functional language for fault-tolerant distributed systems', 5, ARRAY['elixir-lang'], '{"icon":"elixir","color":"#4B275F","tags":["backend","distributed"]}'),
    ('sk_sql',  'se_lang', 'SQL', 'sql', 'Structured query language for relational databases', 5, ARRAY['sql-query'], '{"icon":"sql","color":"#336791","tags":["database","analytics"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- Web Development skills
INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_react','se_web', 'React', 'react', 'UI library for building component-based web applications', 5, ARRAY['reactjs', 'react.js'], '{"icon":"react","color":"#61DAFB","tags":["frontend","ui"]}'),
    ('sk_vue',  'se_web', 'Vue.js', 'vuejs', 'Progressive framework for building user interfaces', 5, ARRAY['vue', 'vue-js'], '{"icon":"vue","color":"#4FC08D","tags":["frontend","ui"]}'),
    ('sk_ang',  'se_web', 'Angular', 'angular', 'TypeScript-based web application framework by Google', 5, ARRAY['angular-js', 'angular2'], '{"icon":"angular","color":"#DD0031","tags":["frontend","enterprise"]}'),
    ('sk_next', 'se_web', 'Next.js', 'nextjs', 'React framework for production with SSR and SSG', 5, ARRAY['next-js'], '{"icon":"nextjs","color":"#000000","tags":["frontend","ssr","ssg"]}'),
    ('sk_nuxt', 'se_web', 'Nuxt.js', 'nuxtjs', 'Vue.js framework for universal applications', 4, ARRAY['nuxt-js'], '{"icon":"nuxt","color":"#00DC82","tags":["frontend","ssr"]}'),
    ('sk_svelt','se_web', 'Svelte', 'svelte', 'Compiler-based UI framework for building web apps', 4, ARRAY['svelte-js'], '{"icon":"svelte","color":"#FF3E00","tags":["frontend","compiler"]}'),
    ('sk_node', 'se_web', 'Node.js', 'nodejs', 'JavaScript runtime for server-side applications', 5, ARRAY['node'], '{"icon":"nodejs","color":"#339933","tags":["backend","runtime"]}'),
    ('sk_expr', 'se_web', 'Express.js', 'expressjs', 'Minimal web framework for Node.js', 4, ARRAY['express'], '{"icon":"express","color":"#000000","tags":["backend","api"]}'),
    ('sk_fast','se_web', 'FastAPI', 'fastapi', 'Modern Python web framework for building APIs', 4, ARRAY['fast-api'], '{"icon":"fastapi","color":"#009688","tags":["backend","api","python"]}'),
    ('sk_django','se_web','Django', 'django', 'High-level Python web framework with batteries included', 4, ARRAY['django-python'], '{"icon":"django","color":"#092E20","tags":["backend","python","monolithic"]}'),
    ('sk_flask','se_web', 'Flask', 'flask', 'Lightweight Python web framework', 4, ARRAY['flask-python'], '{"icon":"flask","color":"#000000","tags":["backend","python","micro"]}'),
    ('sk_graphql','se_web','GraphQL', 'graphql', 'API query language and runtime', 4, ARRAY[], '{"icon":"graphql","color":"#E10098","tags":["api","backend"]}'),
    ('sk_rest', 'se_web', 'REST API Design', 'rest-api-design', 'Architectural style for designing networked applications', 4, ARRAY['restful'], '{"icon":"rest","color":"#25A162","tags":["api","backend","architecture"]}'),
    ('sk_wasm', 'se_web', 'WebAssembly', 'webassembly', 'Binary instruction format for stack-based virtual machines', 4, ARRAY['wasm'], '{"icon":"wasm","color":"#654FF0","tags":["compiler","performance"]}'),
    ('sk_css',  'se_web', 'CSS', 'css', 'Stylesheet language for describing document presentation', 4, ARRAY['css3'], '{"icon":"css","color":"#1572B6","tags":["frontend","styling"]}'),
    ('sk_html', 'se_web', 'HTML', 'html', 'Standard markup language for web documents', 4, ARRAY['html5'], '{"icon":"html","color":"#E34F26","tags":["frontend","markup"]}'),
    ('sk_tail','se_web', 'Tailwind CSS', 'tailwind-css', 'Utility-first CSS framework for rapid UI development', 4, ARRAY['tailwind'], '{"icon":"tailwind","color":"#06B6D4","tags":["frontend","css","utility"]}'),
    ('sk_sass', 'se_web', 'SASS/SCSS', 'sass', 'CSS preprocessor with variables, nesting, and mixins', 3, ARRAY['scss'], '{"icon":"sass","color":"#CC6699","tags":["frontend","css","preprocessor"]}'),
    ('sk_three','se_web', 'Three.js', 'threejs', '3D JavaScript library for WebGL graphics', 4, ARRAY['three-js'], '{"icon":"threejs","color":"#000000","tags":["frontend","3d","graphics"]}'),
    ('sk_d3',   'se_web', 'D3.js', 'd3js', 'Data-driven document library for data visualization', 4, ARRAY['d3-js'], '{"icon":"d3","color":"#F9A03C","tags":["frontend","visualization","data"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- DevOps & Infrastructure skills
INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_dock', 'se_devops', 'Docker', 'docker', 'Container platform for packaging and deploying applications', 5, ARRAY['docker-ee', 'docker-ce'], '{"icon":"docker","color":"#2496ED","tags":["containers","devops"]}'),
    ('sk_k8s',  'se_devops', 'Kubernetes', 'kubernetes', 'Container orchestration platform for production workloads', 5, ARRAY['k8s'], '{"icon":"kubernetes","color":"#326CE5","tags":["containers","orchestration"]}'),
    ('sk_aws',  'se_devops', 'Amazon Web Services', 'aws', 'Cloud computing platform by Amazon', 5, ARRAY['aws-cloud'], '{"icon":"aws","color":"#FF9900","tags":["cloud","infrastructure"]}'),
    ('sk_gcp',  'se_devops', 'Google Cloud Platform', 'gcp', 'Cloud computing services by Google', 4, ARRAY['gcloud', 'google-cloud'], '{"icon":"gcp","color":"#4285F4","tags":["cloud","infrastructure"]}'),
    ('sk_az',   'se_devops', 'Microsoft Azure', 'azure', 'Cloud computing services by Microsoft', 4, ARRAY[], '{"icon":"azure","color":"#0078D4","tags":["cloud","infrastructure"]}'),
    ('sk_ci',   'se_devops', 'CI/CD Pipelines', 'cicd-pipelines', 'Automated build, test, and deployment pipelines', 4, ARRAY['continuous-deployment'], '{"icon":"cicd","color":"#239120","tags":["devops","automation"]}'),
    ('sk_gha',  'se_devops', 'GitHub Actions', 'github-actions', 'GitHub-native CI/CD and workflow automation', 4, ARRAY['gh-actions'], '{"icon":"github-actions","color":"#2088FF","tags":["devops","ci","automation"]}'),
    ('sk_terr', 'se_devops', 'Terraform', 'terraform', 'Infrastructure-as-code tool by HashiCorp', 4, ARRAY['terraform-iac'], '{"icon":"terraform","color":"#7B42BC","tags":["iac","infrastructure"]}'),
    ('sk_ans',  'se_devops', 'Ansible', 'ansible', 'Configuration management and automation tool', 4, ARRAY[], '{"icon":"ansible","color":"#EE0000","tags":["iac","config-mgmt"]}'),
    ('sk_helm', 'se_devops', 'Helm', 'helm', 'Kubernetes package manager', 3, ARRAY['helm-charts'], '{"icon":"helm","color":"#0F1689","tags":["k8s","packaging"]}'),
    ('sk_prom', 'se_devops', 'Prometheus', 'prometheus', 'Monitoring system and time-series database', 3, ARRAY['prom-monitoring'], '{"icon":"prometheus","color":"#E6522C","tags":["monitoring","metrics"]}'),
    ('sk_graf', 'se_devops', 'Grafana', 'grafana', 'Observability and data visualization platform', 3, ARRAY[], '{"icon":"grafana","color":"#F46800","tags":["monitoring","dashboards"]}'),
    ('sk_cloud','se_devops', 'Cloud Architecture', 'cloud-architecture', 'Designing scalable and resilient cloud solutions', 5, ARRAY['cloud-design'], '{"icon":"cloud","color":"#4285F4","tags":["architecture","cloud"]}'),
    ('sk_ngn',  'se_devops', 'Nginx', 'nginx', 'High-performance web server and reverse proxy', 4, ARRAY['nginx-proxy'], '{"icon":"nginx","color":"#009639","tags":["web-server","proxy"]}'),
    ('sk_gita', 'se_devops', 'Git', 'git', 'Distributed version control system', 4, ARRAY['git-vcs'], '{"icon":"git","color":"#F05032","tags":["vcs","collaboration"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- Databases skills
INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_pg',  'se_db', 'PostgreSQL', 'postgresql', 'Advanced open-source relational database', 5, ARRAY['postgres', 'psql'], '{"icon":"postgresql","color":"#336791","tags":["database","relational"]}'),
    ('sk_mys', 'se_db', 'MySQL', 'mysql', 'Popular open-source relational database', 4, ARRAY['mysql-db'], '{"icon":"mysql","color":"#4479A1","tags":["database","relational"]}'),
    ('sk_mong','se_db', 'MongoDB', 'mongodb', 'Document-oriented NoSQL database', 4, ARRAY['mongo'], '{"icon":"mongodb","color":"#47A248","tags":["database","nosql"]}'),
    ('sk_red','se_db', 'Redis', 'redis', 'In-memory data structure store for caching and messaging', 4, ARRAY['redis-cache'], '{"icon":"redis","color":"#DC382D","tags":["database","cache"]}'),
    ('sk_es',  'se_db', 'Elasticsearch', 'elasticsearch', 'Distributed search and analytics engine', 4, ARRAY['es-search'], '{"icon":"elasticsearch","color":"#005571","tags":["database","search","analytics"]}'),
    ('sk_cass','se_db', 'Cassandra', 'cassandra', 'Wide-column NoSQL database for large-scale data', 4, ARRAY['apache-cassandra'], '{"icon":"cassandra","color":"#1287B1","tags":["database","nosql","distributed"]}'),
    ('sk_ddb', 'se_db', 'DynamoDB', 'dynamodb', 'AWS managed NoSQL key-value and document database', 4, ARRAY['dynamodb-aws'], '{"icon":"dynamodb","color":"#4053D6","tags":["database","nosql","aws"]}'),
    ('sk_sqlb','se_db', 'SQLite', 'sqlite', 'Embedded relational database engine', 3, ARRAY[], '{"icon":"sqlite","color":"#003B57","tags":["database","embedded"]}'),
    ('sk_bq',  'se_db', 'BigQuery', 'bigquery', 'Google Cloud serverless data warehouse', 4, ARRAY['big-query'], '{"icon":"bigquery","color":"#669DF6","tags":["database","data-warehouse","gcp"]}'),
    ('sk_click','se_db', 'ClickHouse', 'clickhouse', 'Columnar DBMS for real-time analytics', 3, ARRAY[], '{"icon":"clickhouse","color":"#FCC624","tags":["database","analytics","columnar"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- System Design skills
INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_micr','se_arch', 'Microservices Architecture', 'microservices-architecture', 'Architectural style structuring app as service collection', 5, ARRAY['microservices'], '{"icon":"microservices","color":"#2496ED","tags":["architecture","distributed"]}'),
    ('sk_dsys','se_arch', 'Distributed Systems', 'distributed-systems', 'Systems with components on multiple networked computers', 5, ARRAY['distributed-computing'], '{"icon":"distributed","color":"#E6522C","tags":["architecture","distributed"]}'),
    ('sk_evnt','se_arch', 'Event-Driven Architecture', 'event-driven-architecture', 'Architecture pattern using events for communication', 4, ARRAY['eda'], '{"icon":"events","color":"#FF6F00","tags":["architecture","async"]}'),
    ('sk_mess','se_arch', 'Message Queues (Kafka, RabbitMQ)', 'message-queues', 'Asynchronous messaging systems for event streaming', 4, ARRAY['kafka', 'rabbitmq'], '{"icon":"kafka","color":"#231F20","tags":["architecture","messaging","async"]}'),
    ('sk_cqrs','se_arch', 'CQRS', 'cqrs', 'Command Query Responsibility Segregation pattern', 4, ARRAY[], '{"icon":"cqrs","color":"#9C27B0","tags":["architecture","pattern"]}'),
    ('sk_ddd', 'se_arch', 'Domain-Driven Design', 'domain-driven-design', 'Approach to software design based on domain modeling', 4, ARRAY['ddd'], '{"icon":"ddd","color":"#1565C0","tags":["architecture","design"]}'),
    ('sk_hex', 'se_arch', 'Hexagonal Architecture', 'hexagonal-architecture', 'Ports and adapters architecture pattern', 4, ARRAY['ports-and-adapters'], '{"icon":"hexagon","color":"#43A047","tags":["architecture","pattern"]}'),
    ('sk_test','se_arch', 'Software Testing', 'software-testing', 'Unit, integration, e2e, and performance testing practices', 4, ARRAY['testing', 'tdd'], '{"icon":"testing","color":"#FF5722","tags":["quality","testing"]}'),
    ('sk_perf','se_arch', 'Performance Engineering', 'performance-engineering', 'Profiling, optimization, and benchmarking systems', 4, ARRAY['performance-tuning'], '{"icon":"performance","color":"#E91E63","tags":["architecture","optimization"]}'),
    ('sk_secu','se_arch', 'Security Engineering', 'security-engineering', 'Building secure systems with authentication, authorization, encryption', 4, ARRAY['appsec', 'security'], '{"icon":"security","color":"#4CAF50","tags":["architecture","security"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- =============================================================
-- DOMAIN 2: Data & AI
-- =============================================================

INSERT INTO skill_categories (category_id, name, slug, description, level, sort_order) VALUES
    ('dai_root', 'Data & AI', 'data-ai', 'Data science, machine learning, artificial intelligence, and data engineering', 0, 2)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skill_categories (category_id, parent_category_id, name, slug, description, level, sort_order) VALUES
    ('dai_ds',   'dai_root', 'Data Science', 'data-science', 'Statistical analysis, data visualization, and data-driven decision making', 1, 1),
    ('dai_ml',   'dai_root', 'Machine Learning', 'machine-learning', 'ML algorithms, frameworks, and production MLOps', 1, 2),
    ('dai_dl',   'dai_root', 'Deep Learning', 'deep-learning', 'Neural networks, transformers, computer vision, and NLP', 1, 3),
    ('dai_de',   'dai_root', 'Data Engineering', 'data-engineering', 'Data pipelines, ETL, data warehousing, and streaming', 1, 4),
    ('dai_llm',  'dai_root', 'LLMs & Generative AI', 'llms-generative-ai', 'Large language models, prompt engineering, and AI agents', 1, 5)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_pd',   'dai_ds', 'Pandas', 'pandas', 'Python data manipulation and analysis library', 5, ARRAY['pandas-py'], '{"icon":"pandas","color":"#150458","tags":["data","python"]}'),
    ('sk_np',   'dai_ds', 'NumPy', 'numpy', 'Numerical computing library for Python', 5, ARRAY['numpy-py'], '{"icon":"numpy","color":"#013243","tags":["data","python","math"]}'),
    ('sk_mat','dai_ds', 'Matplotlib', 'matplotlib', 'Python plotting and visualization library', 4, ARRAY['matplotlib-py'], '{"icon":"matplotlib","color":"#11557C","tags":["data","visualization","python"]}'),
    ('sk_seab','dai_ds', 'Seaborn', 'seaborn', 'Statistical data visualization library for Python', 4, ARRAY[], '{"icon":"seaborn","color":"#4B8BBE","tags":["data","visualization","stats"]}'),
    ('sk_plot','dai_ds', 'Plotly', 'plotly', 'Interactive graphing library for Python and JavaScript', 4, ARRAY[], '{"icon":"plotly","color":"#3F4F75","tags":["data","visualization","interactive"]}'),
    ('sk_stat','dai_ds', 'Statistics', 'statistics', 'Descriptive and inferential statistics for data analysis', 5, ARRAY['statistical-analysis'], '{"icon":"stats","color":"#4CAF50","tags":["data","math","foundations"]}'),
    ('sk_prob','dai_ds', 'Probability Theory', 'probability-theory', 'Mathematical framework for modeling uncertainty', 4, ARRAY[], '{"icon":"probability","color":"#9C27B0","tags":["data","math","foundations"]}'),
    ('sk_a_b','dai_ds', 'A/B Testing & Experimentation', 'ab-testing-experimentation', 'Statistical hypothesis testing for product decisions', 4, ARRAY['experiment-design'], '{"icon":"ab-testing","color":"#FF5722","tags":["data","product","experimentation"]}'),
    ('sk_r_l','dai_ds', 'R Language', 'r-language', 'Statistical computing and graphics language', 4, ARRAY['r-stats'], '{"icon":"r","color":"#276DC3","tags":["data","stats","programming"]}'),
    ('sk_tbl','dai_ds', 'Tableau', 'tableau', 'Business intelligence and data visualization platform', 4, ARRAY[], '{"icon":"tableau","color":"#E97627","tags":["data","visualization","bi"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_sci','dai_ml', 'Scikit-Learn', 'scikit-learn', 'Python ML library for classification, regression, clustering', 5, ARRAY['sklearn'], '{"icon":"scikit-learn","color":"#F7931E","tags":["ml","python"]}'),
    ('sk_xgb','dai_ml', 'XGBoost', 'xgboost', 'Gradient boosting framework for ML', 4, ARRAY[], '{"icon":"xgboost","color":"#E65100","tags":["ml","gradient-boosting"]}'),
    ('sk_lgb','dai_ml', 'LightGBM', 'lightgbm', 'Gradient boosting framework with tree-based learning', 4, ARRAY[], '{"icon":"lightgbm","color":"#4B8BBE","tags":["ml","gradient-boosting"]}'),
    ('sk_feat','dai_ml', 'Feature Engineering', 'feature-engineering', 'Creating and selecting features for ML models', 5, ARRAY['feature-selection'], '{"icon":"features","color":"#1565C0","tags":["ml","feature-engineering"]}'),
    ('sk_eval','dai_ml', 'ML Model Evaluation', 'ml-model-evaluation', 'Cross-validation, metrics, bias-variance tradeoff', 5, ARRAY['model-validation'], '{"icon":"evaluation","color":"#E91E63","tags":["ml","evaluation"]}'),
    ('sk_mlo','dai_ml', 'MLOps', 'mlops', 'ML lifecycle management: deployment, monitoring, retraining', 4, ARRAY['ml-ops'], '{"icon":"mlops","color":"#00BCD4","tags":["ml","devops","infrastructure"]}'),
    ('sk_hpt','dai_ml', 'Hyperparameter Tuning', 'hyperparameter-tuning', 'Optimizing ML model hyperparameters for best performance', 4, ARRAY[], '{"icon":"tuning","color":"#FFC107","tags":["ml","optimization"]}'),
    ('sk_exp','dai_ml', 'Experiment Tracking (MLflow)', 'experiment-tracking-mlflow', 'Tracking ML experiments, parameters, and results', 3, ARRAY['mlflow'], '{"icon":"mlflow","color":"#0194E2","tags":["ml","experiments"]}'),
    ('sk_rec','dai_ml', 'Recommendation Systems', 'recommendation-systems', 'Collaborative and content-based recommendation algorithms', 4, ARRAY[], '{"icon":"recommendation","color":"#7B1FA2","tags":["ml","recommender"]}'),
    ('sk_anom','dai_ml', 'Anomaly Detection', 'anomaly-detection', 'Identifying unusual patterns and outliers in data', 4, ARRAY[], '{"icon":"anomaly","color":"#FF5722","tags":["ml","security","monitoring"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_tf', 'dai_dl', 'TensorFlow', 'tensorflow', 'End-to-end ML platform by Google for deep learning', 5, ARRAY['tf-keras'], '{"icon":"tensorflow","color":"#FF6F00","tags":["dl","neural-networks","google"]}'),
    ('sk_pt', 'dai_dl', 'PyTorch', 'pytorch', 'ML framework by Meta with dynamic computation graphs', 5, ARRAY['pytorch-lightning'], '{"icon":"pytorch","color":"#EE4C2C","tags":["dl","neural-networks","meta"]}'),
    ('sk_cnn', 'dai_dl', 'Convolutional Neural Networks', 'cnn', 'Deep learning architecture for image processing', 5, ARRAY['convolutional-nets'], '{"icon":"cnn","color":"#1565C0","tags":["dl","vision","image"]}'),
    ('sk_rnn', 'dai_dl', 'Recurrent Neural Networks', 'rnn', 'Deep learning architecture for sequential data', 4, ARRAY['lstm', 'gru'], '{"icon":"rnn","color":"#7B1FA2","tags":["dl","sequence","nlp"]}'),
    ('sk_trans','dai_dl', 'Transformers', 'transformers', 'Attention-based architecture powering modern NLP and beyond', 5, ARRAY['transformer-model'], '{"icon":"transformers","color":"#E91E63","tags":["dl","nlp","attention"]}'),
    ('sk_cv', 'dai_dl', 'Computer Vision', 'computer-vision', 'Image and video analysis using deep learning', 5, ARRAY['vision'], '{"icon":"cv","color":"#4CAF50","tags":["dl","vision","image"]}'),
    ('sk_nlp', 'dai_dl', 'Natural Language Processing', 'nlp', 'Text processing and understanding with ML/DL', 5, ARRAY['nlp-engineering'], '{"icon":"nlp","color":"#03A9F4","tags":["dl","nlp","text"]}'),
    ('sk_gan', 'dai_dl', 'Generative Adversarial Networks', 'gan', 'Deep learning for realistic synthetic data generation', 4, ARRAY['gans'], '{"icon":"gan","color":"#FF5722","tags":["dl","generative"]}'),
    ('sk_rl',  'dai_dl', 'Reinforcement Learning', 'reinforcement-learning', 'ML paradigm based on agent-environment interaction', 4, ARRAY['rl'], '{"icon":"rl","color":"#673AB7","tags":["dl","agents"]}'),
    ('sk_attn','dai_dl', 'Attention Mechanisms', 'attention-mechanisms', 'Neural network component for focussing on relevant input', 4, ARRAY['self-attention'], '{"icon":"attention","color":"#FF9800","tags":["dl","nlp","architecture"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_spark','dai_de', 'Apache Spark', 'apache-spark', 'Unified analytics engine for large-scale data processing', 5, ARRAY['spark'], '{"icon":"spark","color":"#E25A1C","tags":["big-data","processing"]}'),
    ('sk_etl', 'dai_de', 'ETL Pipelines', 'etl-pipelines', 'Extract, transform, load processes for data warehousing', 5, ARRAY['data-pipelines'], '{"icon":"etl","color":"#9C27B0","tags":["data-engineering","pipelines"]}'),
    ('sk_airf','dai_de', 'Apache Airflow', 'apache-airflow', 'Workflow orchestration platform for data pipelines', 4, ARRAY['airflow'], '{"icon":"airflow","color":"#017CEE","tags":["data-engineering","orchestration"]}'),
    ('sk_beam','dai_de', 'Apache Beam', 'apache-beam', 'Unified model for batch and streaming data processing', 3, ARRAY['beam'], '{"icon":"beam","color":"#003D7A","tags":["data-engineering","streaming"]}'),
    ('sk_flink','dai_de', 'Apache Flink', 'apache-flink', 'Stream processing framework for real-time data', 4, ARRAY['flink'], '{"icon":"flink","color":"#E6522F","tags":["data-engineering","streaming"]}'),
    ('sk_dw',  'dai_de', 'Data Warehousing', 'data-warehousing', 'Architecture for storing and analyzing large datasets', 5, ARRAY['data-warehouse'], '{"icon":"warehouse","color":"#336791","tags":["data-engineering","architecture"]}'),
    ('sk_lake','dai_de', 'Data Lake Architecture', 'data-lake-architecture', 'Storage repository for raw data in native format', 4, ARRAY[], '{"icon":"lake","color":"#1565C0","tags":["data-engineering","architecture"]}'),
    ('sk_iceb','dai_de', 'Apache Iceberg', 'apache-iceberg', 'Open table format for petabyte-scale analytic datasets', 3, ARRAY['iceberg-table'], '{"icon":"iceberg","color":"#3F51B5","tags":["data-engineering","table-format"]}'),
    ('sk_delt','dai_de', 'Delta Lake', 'delta-lake', 'Storage layer for reliable data lakes with ACID', 3, ARRAY[], '{"icon":"deltalake","color":"#003366","tags":["data-engineering","lakehouse"]}'),
    ('sk_dbt', 'dai_de', 'DBT', 'dbt', 'Data build tool for analytics engineering and transformations', 4, ARRAY['data-build-tool'], '{"icon":"dbt","color":"#FF694B","tags":["data-engineering","transformation"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_pe',  'dai_llm', 'Prompt Engineering', 'prompt-engineering', 'Designing and optimizing prompts for LLMs', 5, ARRAY[], '{"icon":"prompt","color":"#FF6F00","tags":["llm","prompting"]}'),
    ('sk_rag', 'dai_llm', 'RAG (Retrieval-Augmented Generation)', 'rag', 'Augmenting LLMs with external knowledge retrieval', 5, ARRAY['retrieval-augmented-generation'], '{"icon":"rag","color":"#4CAF50","tags":["llm","retrieval"]}'),
    ('sk_lngc','dai_llm', 'LangChain', 'langchain', 'Framework for building LLM-powered applications', 4, ARRAY[], '{"icon":"langchain","color":"#1C3C3C","tags":["llm","framework"]}'),
    ('sk_llm','dai_llm', 'LLM Fine-Tuning', 'llm-fine-tuning', 'Fine-tuning large language models for domain adaptation', 5, ARRAY['fine-tuning'], '{"icon":"finetune","color":"#E91E63","tags":["llm","training"]}'),
    ('sk_vecd','dai_llm', 'Vector Databases', 'vector-databases', 'Specialized databases for embedding vector storage and search', 4, ARRAY['vector-search', 'pinecone', 'weaviate', 'qdrant'], '{"icon":"vectordb","color":"#673AB7","tags":["llm","embeddings","search"]}'),
    ('sk_agem','dai_llm', 'AI Agents', 'ai-agents', 'Autonomous agents using LLMs for task execution', 4, ARRAY['agentic-ai'], '{"icon":"agents","color":"#00BCD4","tags":["llm","agents","autonomous"]}'),
    ('sk_lmm','dai_llm', 'LLM Evaluation & Safety', 'llm-evaluation-safety', 'Evaluating LLM outputs, hallucination detection, safety guardrails', 4, ARRAY['llm-safety'], '{"icon":"safety","color":"#FF5722","tags":["llm","evaluation","safety"]}'),
    ('sk_embed','dai_llm', 'Embeddings & Semantic Search', 'embeddings-semantic-search', 'Converting text to vectors for semantic similarity search', 4, ARRAY['semantic-search'], '{"icon":"embeddings","color":"#1565C0","tags":["llm","embeddings","search"]}'),
    ('sk_oll','dai_llm', 'Local LLMs (Ollama)', 'local-llms-ollama', 'Running LLMs locally with tools like Ollama', 3, ARRAY['ollama'], '{"icon":"ollama","color":"#000000","tags":["llm","local","open-source"]}'),
    ('sk_mult','dai_llm', 'Multimodal AI', 'multimodal-ai', 'AI models processing text, images, audio, and video simultaneously', 4, ARRAY[], '{"icon":"multimodal","color":"#9C27B0","tags":["llm","multimodal","vision"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- =============================================================
-- DOMAIN 3: Design
-- =============================================================

INSERT INTO skill_categories (category_id, name, slug, description, level, sort_order) VALUES
    ('des_root', 'Design', 'design', 'UI/UX, product design, visual design, and design systems', 0, 3)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skill_categories (category_id, parent_category_id, name, slug, description, level, sort_order) VALUES
    ('des_ux',   'des_root', 'UX Design', 'ux-design', 'User research, usability, information architecture, and interaction design', 1, 1),
    ('des_ui',   'des_root', 'UI Design', 'ui-design', 'Visual interface design, component libraries, and design systems', 1, 2),
    ('des_mot',  'des_root', 'Motion Design', 'motion-design', 'Animation, micro-interactions, and Lottie', 1, 3)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_ur',  'des_ux', 'User Research', 'user-research', 'Qualitative and quantitative methods for understanding users', 5, ARRAY['ux-research'], '{"icon":"research","color":"#1565C0","tags":["ux","research"]}'),
    ('sk_ia',  'des_ux', 'Information Architecture', 'information-architecture', 'Organizing content and navigation for usability', 4, ARRAY[], '{"icon":"ia","color":"#4CAF50","tags":["ux","architecture"]}'),
    ('sk_wire','des_ux', 'Wireframing & Prototyping', 'wireframing-prototyping', 'Creating low and high-fidelity interface mockups', 5, ARRAY[], '{"icon":"wireframe","color":"#FF9800","tags":["ux","prototyping"]}'),
    ('sk_usa','des_ux', 'Usability Testing', 'usability-testing', 'Evaluating products by testing with representative users', 4, ARRAY[], '{"icon":"usability","color":"#E91E63","tags":["ux","testing","research"]}'),
    ('sk_dt',  'des_ux', 'Design Thinking', 'design-thinking', 'Human-centered problem-solving methodology', 4, ARRAY[], '{"icon":"design-thinking","color":"#9C27B0","tags":["ux","methodology"]}'),
    ('sk_a11y','des_ux', 'Accessibility (a11y)', 'accessibility', 'Designing for users with disabilities (WCAG)', 4, ARRAY['wcag'], '{"icon":"a11y","color":"#00BCD4","tags":["ux","accessibility","inclusion"]}'),
    ('sk_ser','des_ux', 'Service Design', 'service-design', 'Designing and orchestrating end-to-end service experiences', 3, ARRAY[], '{"icon":"service","color":"#3F51B5","tags":["ux","service"]}'),
    ('sk_jtbd','des_ux', 'Jobs-to-be-Done', 'jobs-to-be-done', 'Framework for understanding user needs and motivations', 3, ARRAY['jtbd'], '{"icon":"jtbd","color":"#795548","tags":["ux","product","research"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_fig','des_ui', 'Figma', 'figma', 'Collaborative interface design tool', 5, ARRAY[], '{"icon":"figma","color":"#F24E1E","tags":["ui","design-tool"]}'),
    ('sk_sys','des_ui', 'Design Systems', 'design-systems', 'Creating and maintaining reusable component libraries', 5, ARRAY[], '{"icon":"design-system","color":"#1565C0","tags":["ui","systems","components"]}'),
    ('sk_typo','des_ui', 'Typography', 'typography', 'Art of arranging type for readability and aesthetics', 4, ARRAY[], '{"icon":"typography","color":"#4CAF50","tags":["ui","visual"]}'),
    ('sk_col','des_ui', 'Color Theory', 'color-theory', 'Understanding color relationships and accessibility', 4, ARRAY[], '{"icon":"color","color":"#E91E63","tags":["ui","visual"]}'),
    ('sk_bra','des_ui', 'Brand Identity Design', 'brand-identity-design', 'Creating visual identities and brand systems', 4, ARRAY['branding'], '{"icon":"brand","color":"#9C27B0","tags":["ui","brand"]}'),
    ('sk_mate','des_ui', 'Material Design', 'material-design', 'Google design system for digital interfaces', 3, ARRAY[], '{"icon":"material","color":"#2196F3","tags":["ui","design-system","google"]}'),
    ('sk_sket','des_ui', 'Sketch', 'sketch', 'Vector-based design tool for macOS', 3, ARRAY[], '{"icon":"sketch","color":"#F7B500","tags":["ui","design-tool"]}'),
    ('sk_adob','des_ui', 'Adobe Creative Suite', 'adobe-creative-suite', 'Photoshop, Illustrator, XD, After Effects for design', 4, ARRAY['photoshop', 'illustrator', 'xd'], '{"icon":"adobe","color":"#FF0000","tags":["ui","design-tool","graphics"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_moti','des_mot', 'Motion Graphics', 'motion-graphics', 'Animated graphic design for video and web', 5, ARRAY[], '{"icon":"motion","color":"#FF5722","tags":["motion","animation"]}'),
    ('sk_micr','des_mot', 'Micro-Interactions', 'micro-interactions', 'Small functional animations that enhance user experience', 4, ARRAY[], '{"icon":"micro","color":"#00BCD4","tags":["motion","ux","interaction"]}'),
    ('sk_lott','des_mot', 'Lottie', 'lottie', 'Open-source animation file format from Airbnb', 3, ARRAY['lottie-files'], '{"icon":"lottie","color":"#00D084","tags":["motion","animation","json"]}'),
    ('sk_rm','des_mot', 'Rive', 'rive', 'Real-time interactive animation tool for apps and games', 3, ARRAY[], '{"icon":"rive","color":"#6D28D9","tags":["motion","interactive","animation"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- =============================================================
-- DOMAIN 4: Product & Business
-- =============================================================

INSERT INTO skill_categories (category_id, name, slug, description, level, sort_order) VALUES
    ('prb_root', 'Product & Business', 'product-business', 'Product management, entrepreneurship, marketing, and strategy', 0, 4)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skill_categories (category_id, parent_category_id, name, slug, description, level, sort_order) VALUES
    ('prb_pm',  'prb_root', 'Product Management', 'product-management', 'Product strategy, roadmapping, prioritization, and stakeholder management', 1, 1),
    ('prb_ent', 'prb_root', 'Entrepreneurship', 'entrepreneurship', 'Startup building, fundraising, growth, and business operations', 1, 2),
    ('prb_mkt', 'prb_root', 'Marketing & Growth', 'marketing-growth', 'Digital marketing, content strategy, SEO, and growth hacking', 1, 3),
    ('prb_str', 'prb_root', 'Strategy & Leadership', 'strategy-leadership', 'Business strategy, team leadership, and organizational design', 1, 4)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_prod','prb_pm', 'Product Strategy', 'product-strategy', 'Defining product vision, strategy, and OKRs', 5, ARRAY['product-vision'], '{"icon":"strategy","color":"#1565C0","tags":["product","strategy"]}'),
    ('sk_road','prb_pm', 'Roadmapping', 'roadmapping', 'Planning and communicating product development timelines', 4, ARRAY['product-roadmap'], '{"icon":"roadmap","color":"#4CAF50","tags":["product","planning"]}'),
    ('sk_prio','prb_pm', 'Prioritization Frameworks', 'prioritization-frameworks', 'RICE, ICE, MoSCoW, value-vs-effort matrices', 4, ARRAY['rice', 'moscow'], '{"icon":"prioritize","color":"#FF9800","tags":["product","prioritization"]}'),
    ('sk_spr','prb_pm', 'Sprint Planning & Agile', 'sprint-planning-agile', 'Agile methodologies: Scrum, Kanban, sprint ceremonies', 4, ARRAY['scrum', 'kanban'], '{"icon":"agile","color":"#00BCD4","tags":["product","agile","process"]}'),
    ('sk_stk','prb_pm', 'Stakeholder Management', 'stakeholder-management', 'Communicating with executives, engineers, and customers', 4, ARRAY[], '{"icon":"stakeholder","color":"#9C27B0","tags":["product","communication"]}'),
    ('sk_data','prb_pm', 'Data-Driven Product Decisions', 'data-driven-product-decisions', 'Using metrics, funnels, and product analytics to drive decisions', 5, ARRAY['product-analytics'], '{"icon":"analytics","color":"#E91E63","tags":["product","data","decisions"]}'),
    ('sk_pmr','prb_pm', 'Product-Market Fit', 'product-market-fit', 'Finding and measuring product-market fit for new products', 4, ARRAY['pmf'], '{"icon":"pmf","color":"#FF5722","tags":["product","pmf","growth"]}'),
    ('sk_prd','prb_pm', 'PRD Writing', 'prd-writing', 'Writing clear product requirement documents and specs', 4, ARRAY['product-requirements'], '{"icon":"prd","color":"#795548","tags":["product","documentation"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_stf','prb_ent', 'Startup Fundamentals', 'startup-fundamentals', 'Building a company from idea to early traction', 5, ARRAY[], '{"icon":"startup","color":"#000000","tags":["entrepreneurship","startup"]}'),
    ('sk_fun','prb_ent', 'Fundraising', 'fundraising', 'Raising capital: seed, Series A, pitch decks, and investor relations', 4, ARRAY['venture-capital'], '{"icon":"fundraising","color":"#4CAF50","tags":["entrepreneurship","finance"]}'),
    ('sk_bp', 'prb_ent', 'Business Modeling', 'business-modeling', 'Creating and validating business models and revenue streams', 4, ARRAY['business-model-canvas'], '{"icon":"business-model","color":"#1565C0","tags":["entrepreneurship","business"]}'),
    ('sk_fn', 'prb_ent', 'Financial Planning', 'financial-planning', 'Budgeting, forecasting, unit economics, and P&L management', 4, ARRAY['unit-economics'], '{"icon":"finance","color":"#E91E63","tags":["entrepreneurship","finance"]}'),
    ('sk_gr','prb_ent', 'Growth Hacking', 'growth-hacking', 'Experiment-driven strategies for rapid user acquisition', 4, ARRAY[], '{"icon":"growth","color":"#FF5722","tags":["entrepreneurship","growth","marketing"]}'),
    ('sk_leg','prb_ent', 'Legal Fundamentals for Startups', 'legal-fundamentals-startups', 'IP, incorporation, contracts, and compliance basics', 3, ARRAY[], '{"icon":"legal","color":"#9C27B0","tags":["entrepreneurship","legal"]}'),
    ('sk_sal','prb_ent', 'Sales & Negotiation', 'sales-negotiation', 'B2B and B2C sales, closing deals, and negotiation tactics', 4, ARRAY[], '{"icon":"sales","color":"#00BCD4","tags":["entrepreneurship","sales"]}'),
    ('sk_net','prb_ent', 'Networking & Partnerships', 'networking-partnerships', 'Building professional relationships and strategic partnerships', 3, ARRAY[], '{"icon":"network","color":"#3F51B5","tags":["entrepreneurship","networking"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_seo','prb_mkt', 'SEO', 'seo', 'Search engine optimization for organic traffic', 4, ARRAY['search-engine-optimization'], '{"icon":"seo","color":"#1565C0","tags":["marketing","seo"]}'),
    ('sk_smm','prb_mkt', 'Social Media Marketing', 'social-media-marketing', 'Managing and growing brand presence on social platforms', 4, ARRAY[], '{"icon":"social","color":"#E91E63","tags":["marketing","social"]}'),
    ('sk_con','prb_mkt', 'Content Marketing', 'content-marketing', 'Creating valuable content to attract and retain audiences', 4, ARRAY[], '{"icon":"content","color":"#FF9800","tags":["marketing","content"]}'),
    ('sk_em','prb_mkt', 'Email Marketing', 'email-marketing', 'Email campaigns, automation, and list management', 4, ARRAY[], '{"icon":"email","color":"#4CAF50","tags":["marketing","email"]}'),
    ('sk_ppc','prb_mkt', 'PPC & Paid Advertising', 'ppc-paid-advertising', 'Paid search, display ads, and social media advertising', 4, ARRAY['google-ads'], '{"icon":"ppc","color":"#9C27B0","tags":["marketing","ads"]}'),
    ('sk_an','prb_mkt', 'Marketing Analytics', 'marketing-analytics', 'Measuring campaign performance, attribution, and ROI', 4, ARRAY[], '{"icon":"analytics","color":"#00BCD4","tags":["marketing","analytics"]}'),
    ('sk_cro','prb_mkt', 'Conversion Rate Optimization', 'cro', 'Improving website and landing page conversion rates', 3, ARRAY['cro'], '{"icon":"cro","color":"#FF5722","tags":["marketing","optimization"]}'),
    ('sk_inf','prb_mkt', 'Influencer Marketing', 'influencer-marketing', 'Leveraging influencers for brand awareness and trust', 3, ARRAY[], '{"icon":"influencer","color":"#E040FB","tags":["marketing","influencer"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_ops','prb_str', 'Business Operations', 'business-operations', 'Running day-to-day business processes and operations', 4, ARRAY[], '{"icon":"ops","color":"#1565C0","tags":["strategy","operations"]}'),
    ('sk_hr','prb_str', 'Team Building & HR', 'team-building-hr', 'Hiring, onboarding, performance management, and culture', 4, ARRAY[], '{"icon":"hr","color":"#4CAF50","tags":["strategy","people"]}'),
    ('sk_lead','prb_str', 'Leadership', 'leadership', 'Leading teams, decision-making, and executive presence', 5, ARRAY[], '{"icon":"leadership","color":"#9C27B0","tags":["strategy","leadership","people"]}'),
    ('sk_comm','prb_str', 'Communication', 'communication', 'Written and verbal communication for business contexts', 4, ARRAY[], '{"icon":"communication","color":"#00BCD4","tags":["strategy","communication"]}'),
    ('sk_neg','prb_str', 'Negotiation', 'negotiation', 'Negotiating contracts, salaries, and partnerships', 4, ARRAY[], '{"icon":"negotiation","color":"#FF5722","tags":["strategy","negotiation"]}'),
    ('sk_org','prb_str', 'Organizational Design', 'organizational-design', 'Structuring teams and organizations for effectiveness', 3, ARRAY[], '{"icon":"org-design","color":"#E91E63","tags":["strategy","organization"]}'),
    ('sk_chg','prb_str', 'Change Management', 'change-management', 'Leading organizational change and transformation', 3, ARRAY[], '{"icon":"change","color":"#FF9800","tags":["strategy","change"]}'),
    ('sk_cr','prb_str', 'Conflict Resolution', 'conflict-resolution', 'Mediating disputes and maintaining team harmony', 3, ARRAY[], '{"icon":"conflict","color":"#795548","tags":["strategy","people"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- =============================================================
-- DOMAIN 5: Cybersecurity
-- =============================================================

INSERT INTO skill_categories (category_id, name, slug, description, level, sort_order) VALUES
    ('sec_root', 'Cybersecurity', 'cybersecurity', 'Security engineering, compliance, threat intelligence, and governance', 0, 5)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skill_categories (category_id, parent_category_id, name, slug, description, level, sort_order) VALUES
    ('sec_eng', 'sec_root', 'Security Engineering', 'security-engineering', 'AppSec, network security, cryptography, and identity management', 1, 1),
    ('sec_cmp', 'sec_root', 'Compliance & Governance', 'compliance-governance', 'SOC 2, GDPR, ISO 27001, NIST, and security frameworks', 1, 2),
    ('sec_thr', 'sec_root', 'Threat Intelligence', 'threat-intelligence', 'Threat hunting, forensics, incident response, and CTI', 1, 3),
    ('sec_pri', 'sec_root', 'Privacy & Data Protection', 'privacy-data-protection', 'Data privacy regulations, encryption, and data governance', 1, 4)
ON CONFLICT (name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_appsec','sec_eng', 'Application Security (AppSec)', 'application-security', 'Securing software throughout the SDLC', 5, ARRAY['appsec'], '{"icon":"appsec","color":"#E91E63","tags":["security","engineering"]}'),
    ('sk_netsec','sec_eng', 'Network Security', 'network-security', 'Firewalls, VPNs, intrusion detection, and network segmentation', 5, ARRAY[], '{"icon":"network","color":"#1565C0","tags":["security","network"]}'),
    ('sk_crypto','sec_eng', 'Cryptography', 'cryptography', 'Encryption, hashing, PKI, and cryptographic protocols', 5, ARRAY['crypto'], '{"icon":"crypto","color":"#FF9800","tags":["security","cryptography"]}'),
    ('sk_authz','sec_eng', 'Authentication & Authorization', 'authentication-authorization', 'OAuth, SAML, JWT, SSO, and identity management', 5, ARRAY['auth', 'oauth'], '{"icon":"auth","color":"#4CAF50","tags":["security","identity"]}'),
    ('sk_cloudsec','sec_eng', 'Cloud Security', 'cloud-security', 'Securing cloud infrastructure (AWS, GCP, Azure)', 4, ARRAY[], '{"icon":"cloud-sec","color":"#00BCD4","tags":["security","cloud"]}'),
    ('sk_zero','sec_eng', 'Zero Trust Architecture', 'zero-trust', 'Security model assuming no implicit trust', 4, ARRAY[], '{"icon":"zero-trust","color":"#9C27B0","tags":["security","architecture"]}'),
    ('sk_devsec','sec_eng', 'DevSecOps', 'devsecops', 'Integrating security into CI/CD pipelines', 4, ARRAY[], '{"icon":"devsecops","color":"#FF5722","tags":["security","devops"]}'),
    ('sk_sast','sec_eng', 'SAST/DAST', 'sast-dast', 'Static and dynamic application security testing', 4, ARRAY[], '{"icon":"sast","color":"#3F51B5","tags":["security","testing"]}'),
    ('sk_k8sec','sec_eng', 'Kubernetes Security', 'kubernetes-security', 'Securing container orchestration platforms', 3, ARRAY[], '{"icon":"k8s-sec","color":"#326CE5","tags":["security","k8s","containers"]}'),
    ('sk_binary','sec_eng', 'Binary Exploitation', 'binary-exploitation', 'Reverse engineering, buffer overflows, and exploit development', 4, ARRAY['pwning'], '{"icon":"binary","color":"#000000","tags":["security","exploit"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_soc2','sec_cmp', 'SOC 2 Compliance', 'soc-2-compliance', 'SOC 2 Type I and Type II compliance management', 5, ARRAY[], '{"icon":"soc2","color":"#1565C0","tags":["compliance","soc2"]}'),
    ('sk_gdpr','sec_cmp', 'GDPR Compliance', 'gdpr-compliance', 'General Data Protection Regulation compliance', 4, ARRAY[], '{"icon":"gdpr","color":"#4CAF50","tags":["compliance","privacy"]}'),
    ('sk_iso','sec_cmp', 'ISO 27001', 'iso-27001', 'Information security management standard', 4, ARRAY[], '{"icon":"iso","color":"#FF9800","tags":["compliance","isms"]}'),
    ('sk_nist','sec_cmp', 'NIST Cybersecurity Framework', 'nist-csf', 'US government cybersecurity framework', 4, ARRAY['nist-csf'], '{"icon":"nist","color":"#00BCD4","tags":["compliance","framework"]}'),
    ('sk_pci','sec_cmp', 'PCI DSS', 'pci-dss', 'Payment card industry data security standard', 3, ARRAY[], '{"icon":"pci","color":"#E91E63","tags":["compliance","payments"]}'),
    ('sk_hipaa','sec_cmp', 'HIPAA Compliance', 'hipaa-compliance', 'Healthcare data privacy and security regulations', 3, ARRAY[], '{"icon":"hipaa","color":"#9C27B0","tags":["compliance","healthcare"]}'),
    ('sk_audit','sec_cmp', 'Security Auditing', 'security-auditing', 'Conducting and managing security audits', 4, ARRAY[], '{"icon":"audit","color":"#795548","tags":["compliance","auditing"]}'),
    ('sk_pol','sec_cmp', 'Security Policy Development', 'security-policy-development', 'Creating and enforcing security policies and standards', 4, ARRAY[], '{"icon":"policy","color":"#3F51B5","tags":["compliance","policy"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_ir', 'sec_thr', 'Incident Response', 'incident-response', 'Detecting, containing, and remediating security incidents', 5, ARRAY['ir'], '{"icon":"ir","color":"#E91E63","tags":["threat","response"]}'),
    ('sk_for','sec_thr', 'Digital Forensics', 'digital-forensics', 'Collecting and analyzing digital evidence', 4, ARRAY[], '{"icon":"forensics","color":"#1565C0","tags":["threat","forensics"]}'),
    ('sk_thun','sec_thr', 'Threat Hunting', 'threat-hunting', 'Proactively searching for threats in networks and systems', 4, ARRAY[], '{"icon":"hunting","color":"#FF5722","tags":["threat","hunting"]}'),
    ('sk_osint','sec_thr', 'OSINT', 'osint', 'Open-source intelligence gathering and analysis', 4, ARRAY[], '{"icon":"osint","color":"#4CAF50","tags":["threat","intelligence"]}'),
    ('sk_cti','sec_thr', 'Cyber Threat Intelligence', 'cyber-threat-intelligence', 'Collecting and analyzing threat intelligence data', 4, ARRAY['cti'], '{"icon":"cti","color":"#9C27B0","tags":["threat","intelligence"]}'),
    ('sk_mal','sec_thr', 'Malware Analysis', 'malware-analysis', 'Reverse engineering and analyzing malicious software', 4, ARRAY[], '{"icon":"malware","color":"#000000","tags":["threat","analysis"]}'),
    ('sk_red','sec_thr', 'Red Teaming', 'red-teaming', 'Simulating real-world attacks to test defenses', 4, ARRAY['red-team'], '{"icon":"redteam","color":"#E91E63","tags":["threat","testing"]}'),
    ('sk_soc','sec_thr', 'SOC Operations', 'soc-operations', 'Running security operations centers effectively', 3, ARRAY['soc'], '{"icon":"soc","color":"#00BCD4","tags":["threat","operations"]}')
ON CONFLICT (category_id, name) DO NOTHING;

INSERT INTO skills (skill_id, category_id, name, slug, description, level_max, aliases, metadata) VALUES
    ('sk_dlp','sec_pri', 'Data Loss Prevention', 'data-loss-prevention', 'Preventing unauthorized data exfiltration', 4, ARRAY['dlp'], '{"icon":"dlp","color":"#E91E63","tags":["privacy","data"]}'),
    ('sk_dg','sec_pri', 'Data Governance', 'data-governance', 'Managing data availability, usability, integrity, and security', 4, ARRAY[], '{"icon":"governance","color":"#1565C0","tags":["privacy","governance"]}'),
    ('sk_enc','sec_pri', 'Encryption', 'encryption', 'Symmetric and asymmetric encryption, TLS, and key management', 4, ARRAY[], '{"icon":"encryption","color":"#4CAF50","tags":["privacy","cryptography"]}'),
    ('sk_anon','sec_pri', 'Data Anonymization', 'data-anonymization', 'Techniques for de-identifying personal data', 3, ARRAY[], '{"icon":"anonymize","color":"#9C27B0","tags":["privacy","data"]}'),
    ('sk_cpra','sec_pri', 'Data Privacy Regulations (CCPA, DPDP)', 'data-privacy-regulations', 'Global privacy regulations beyond GDPR', 3, ARRAY['ccpa', 'dpdp'], '{"icon":"privacy","color":"#FF9800","tags":["privacy","compliance"]}'),
    ('sk_consent','sec_pri', 'Consent Management', 'consent-management', 'Managing user consent for data collection and processing', 3, ARRAY[], '{"icon":"consent","color":"#00BCD4","tags":["privacy","consent"]}')
ON CONFLICT (category_id, name) DO NOTHING;

-- =============================================================
-- Tags
-- =============================================================

INSERT INTO tags (tag_id, name, slug, description, color) VALUES
    ('tg_beginner', 'beginner', 'beginner', 'Entry-level skills suitable for newcomers', '#4CAF50'),
    ('tg_interm',   'intermediate', 'intermediate', 'Mid-level skills requiring some experience', '#FF9800'),
    ('tg_advanced', 'advanced', 'advanced', 'Expert-level skills requiring deep knowledge', '#E91E63'),
    ('tg_cloud',    'cloud-native', 'cloud-native', 'Skills related to cloud computing and cloud-native technologies', '#4285F4'),
    ('tg_opensource','open-source', 'open-source', 'Skills related to open-source tools and frameworks', '#F05032'),
    ('tg_enterprise','enterprise', 'enterprise', 'Skills commonly used in enterprise environments', '#1565C0'),
    ('tg_emerging', 'emerging', 'emerging', 'Rapidly growing skills with increasing market demand', '#00BCD4'),
    ('tg_mobile',   'mobile', 'mobile', 'Skills related to mobile app development', '#7B1FA2'),
    ('tg_data',     'data-intensive', 'data-intensive', 'Skills for working with large-scale data systems', '#336791'),
    ('tg_ai',       'ai-ml', 'ai-ml', 'Skills related to artificial intelligence and machine learning', '#EE4C2C'),
    ('tg_frontend', 'frontend', 'frontend', 'Client-side and UI development skills', '#61DAFB'),
    ('tg_backend',  'backend', 'backend', 'Server-side and API development skills', '#339933'),
    ('tg_fullstack','fullstack', 'fullstack', 'Skills spanning both frontend and backend development', '#9C27B0'),
    ('tg_devops',   'devops', 'devops', 'Skills related to DevOps practices and tools', '#2496ED'),
    ('tg_security', 'security', 'security', 'Skills related to cybersecurity and secure development', '#E91E63')
ON CONFLICT (name) DO NOTHING;

-- =============================================================
-- Skill-Tag Associations (representative subset)
-- =============================================================

WITH skill_data AS (
    SELECT skill_id, name FROM skills
), tag_data AS (
    SELECT tag_id, slug FROM tags
)
INSERT INTO skill_tags (skill_id, tag_id)
SELECT s.skill_id, t.tag_id
FROM skill_data s, tag_data t
WHERE (s.name IN ('Python', 'Go', 'Rust') AND t.slug = 'backend')
   OR (s.name IN ('React', 'Vue.js', 'Angular', 'Svelte', 'CSS', 'HTML') AND t.slug = 'frontend')
   OR (s.name IN ('Next.js', 'TypeScript') AND t.slug = 'fullstack')
   OR (s.name IN ('Docker', 'Kubernetes', 'Terraform', 'Ansible', 'CI/CD Pipelines', 'GitHub Actions') AND t.slug = 'devops')
   OR (s.name IN ('PostgreSQL', 'MongoDB', 'Elasticsearch') AND t.slug = 'data-intensive')
   OR (s.name IN ('TensorFlow', 'PyTorch', 'Scikit-Learn', 'Transformers') AND t.slug = 'ai-ml')
   OR (s.name IN ('Prompt Engineering', 'RAG (Retrieval-Augmented Generation)', 'LangChain', 'Vector Databases') AND t.slug = 'emerging')
   OR (s.name IN ('Cloud Architecture', 'Amazon Web Services', 'Google Cloud Platform', 'Microsoft Azure') AND t.slug = 'cloud-native')
   OR (s.name IN ('Application Security (AppSec)', 'Network Security', 'Cryptography', 'Incident Response') AND t.slug = 'security')
   OR (s.name IN ('SOC 2 Compliance', 'GDPR Compliance', 'ISO 27001') AND t.slug = 'enterprise')
ON CONFLICT DO NOTHING;

-- =============================================================
-- Skill Relationships (representative prerequisite graph)
-- =============================================================

INSERT INTO skill_relationships (from_skill_id, to_skill_id, relationship_type, weight) VALUES
    -- Python → ML/DL chain
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'Pandas'), 'prerequisite', 1.0),
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'NumPy'), 'prerequisite', 1.0),
    ((SELECT skill_id FROM skills WHERE name = 'Pandas'), (SELECT skill_id FROM skills WHERE name = 'Scikit-Learn'), 'prerequisite', 0.9),
    ((SELECT skill_id FROM skills WHERE name = 'NumPy'), (SELECT skill_id FROM skills WHERE name = 'Scikit-Learn'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'Scikit-Learn'), (SELECT skill_id FROM skills WHERE name = 'TensorFlow'), 'recommended_before', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Scikit-Learn'), (SELECT skill_id FROM skills WHERE name = 'PyTorch'), 'recommended_before', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'FastAPI'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'Django'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'Flask'), 'prerequisite', 0.7),

    -- JavaScript → Web framework chain
    ((SELECT skill_id FROM skills WHERE name = 'JavaScript'), (SELECT skill_id FROM skills WHERE name = 'TypeScript'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'JavaScript'), (SELECT skill_id FROM skills WHERE name = 'React'), 'prerequisite', 1.0),
    ((SELECT skill_id FROM skills WHERE name = 'TypeScript'), (SELECT skill_id FROM skills WHERE name = 'React'), 'recommended_before', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'React'), (SELECT skill_id FROM skills WHERE name = 'Next.js'), 'prerequisite', 1.0),
    ((SELECT skill_id FROM skills WHERE name = 'React'), (SELECT skill_id FROM skills WHERE name = 'GraphQL'), 'recommended_before', 0.4),
    ((SELECT skill_id FROM skills WHERE name = 'JavaScript'), (SELECT skill_id FROM skills WHERE name = 'Node.js'), 'prerequisite', 0.9),
    ((SELECT skill_id FROM skills WHERE name = 'Node.js'), (SELECT skill_id FROM skills WHERE name = 'Express.js'), 'prerequisite', 1.0),
    ((SELECT skill_id FROM skills WHERE name = 'CSS'), (SELECT skill_id FROM skills WHERE name = 'Tailwind CSS'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'CSS'), (SELECT skill_id FROM skills WHERE name = 'SASS/SCSS'), 'prerequisite', 0.5),

    -- Docker → Kubernetes chain
    ((SELECT skill_id FROM skills WHERE name = 'Docker'), (SELECT skill_id FROM skills WHERE name = 'Kubernetes'), 'prerequisite', 1.0),
    ((SELECT skill_id FROM skills WHERE name = 'Kubernetes'), (SELECT skill_id FROM skills WHERE name = 'Helm'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'Terraform'), (SELECT skill_id FROM skills WHERE name = 'Cloud Architecture'), 'complementary', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Docker'), (SELECT skill_id FROM skills WHERE name = 'CI/CD Pipelines'), 'complementary', 0.5),
    ((SELECT skill_id FROM skills WHERE name = 'Kubernetes'), (SELECT skill_id FROM skills WHERE name = 'Prometheus'), 'complementary', 0.5),

    -- SQL → Database specific
    ((SELECT skill_id FROM skills WHERE name = 'SQL'), (SELECT skill_id FROM skills WHERE name = 'PostgreSQL'), 'prerequisite', 0.9),
    ((SELECT skill_id FROM skills WHERE name = 'SQL'), (SELECT skill_id FROM skills WHERE name = 'MySQL'), 'prerequisite', 0.8),

    -- System Design
    ((SELECT skill_id FROM skills WHERE name = 'Microservices Architecture'), (SELECT skill_id FROM skills WHERE name = 'Distributed Systems'), 'related_to', 0.9),
    ((SELECT skill_id FROM skills WHERE name = 'Message Queues (Kafka, RabbitMQ)'), (SELECT skill_id FROM skills WHERE name = 'Event-Driven Architecture'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Domain-Driven Design'), (SELECT skill_id FROM skills WHERE name = 'Microservices Architecture'), 'recommended_before', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'CQRS'), (SELECT skill_id FROM skills WHERE name = 'Event-Driven Architecture'), 'variant_of', 0.5),

    -- ML → DL chain
    ((SELECT skill_id FROM skills WHERE name = 'Statistics'), (SELECT skill_id FROM skills WHERE name = 'Scikit-Learn'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Statistics'), (SELECT skill_id FROM skills WHERE name = 'Feature Engineering'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'TensorFlow'), (SELECT skill_id FROM skills WHERE name = 'Transformers'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'TensorFlow'), (SELECT skill_id FROM skills WHERE name = 'Computer Vision'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'PyTorch'), (SELECT skill_id FROM skills WHERE name = 'Transformers'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'PyTorch'), (SELECT skill_id FROM skills WHERE name = 'Natural Language Processing'), 'prerequisite', 0.7),

    -- LLM chain
    ((SELECT skill_id FROM skills WHERE name = 'Transformers'), (SELECT skill_id FROM skills WHERE name = 'Prompt Engineering'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Prompt Engineering'), (SELECT skill_id FROM skills WHERE name = 'RAG (Retrieval-Augmented Generation)'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'LangChain'), (SELECT skill_id FROM skills WHERE name = 'AI Agents'), 'prerequisite', 0.8),

    -- Cybersecurity chain
    ((SELECT skill_id FROM skills WHERE name = 'Network Security'), (SELECT skill_id FROM skills WHERE name = 'Cloud Security'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Application Security (AppSec)'), (SELECT skill_id FROM skills WHERE name = 'DevSecOps'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Digital Forensics'), (SELECT skill_id FROM skills WHERE name = 'Incident Response'), 'complementary', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'Cryptography'), (SELECT skill_id FROM skills WHERE name = 'Encryption'), 'related_to', 0.9),
    ((SELECT skill_id FROM skills WHERE name = 'SOC 2 Compliance'), (SELECT skill_id FROM skills WHERE name = 'Security Auditing'), 'complementary', 0.7),

    -- Data engineering chain
    ((SELECT skill_id FROM skills WHERE name = 'SQL'), (SELECT skill_id FROM skills WHERE name = 'Data Warehousing'), 'prerequisite', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'Apache Spark'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Data Warehousing'), (SELECT skill_id FROM skills WHERE name = 'Data Lake Architecture'), 'related_to', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'ETL Pipelines'), (SELECT skill_id FROM skills WHERE name = 'Apache Airflow'), 'complementary', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'Apache Spark'), (SELECT skill_id FROM skills WHERE name = 'Apache Flink'), 'similar_to', 0.5),

    -- Product chain
    ((SELECT skill_id FROM skills WHERE name = 'Product Strategy'), (SELECT skill_id FROM skills WHERE name = 'Roadmapping'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Design Thinking'), (SELECT skill_id FROM skills WHERE name = 'Product Strategy'), 'recommended_before', 0.5),
    ((SELECT skill_id FROM skills WHERE name = 'User Research'), (SELECT skill_id FROM skills WHERE name = 'Data-Driven Product Decisions'), 'complementary', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Startup Fundamentals'), (SELECT skill_id FROM skills WHERE name = 'Fundraising'), 'prerequisite', 0.8),
    ((SELECT skill_id FROM skills WHERE name = 'Business Modeling'), (SELECT skill_id FROM skills WHERE name = 'Financial Planning'), 'complementary', 0.6),

    -- Design chain
    ((SELECT skill_id FROM skills WHERE name = 'Color Theory'), (SELECT skill_id FROM skills WHERE name = 'Brand Identity Design'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Wireframing & Prototyping'), (SELECT skill_id FROM skills WHERE name = 'Usability Testing'), 'complementary', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'User Research'), (SELECT skill_id FROM skills WHERE name = 'Design Thinking'), 'complementary', 0.7),
    ((SELECT skill_id FROM skills WHERE name = 'Typography'), (SELECT skill_id FROM skills WHERE name = 'Design Systems'), 'prerequisite', 0.5),

    -- Cross-domain
    ((SELECT skill_id FROM skills WHERE name = 'Design Thinking'), (SELECT skill_id FROM skills WHERE name = 'Product-Market Fit'), 'related_to', 0.4),
    ((SELECT skill_id FROM skills WHERE name = 'Python'), (SELECT skill_id FROM skills WHERE name = 'Machine Learning'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'CI/CD Pipelines'), (SELECT skill_id FROM skills WHERE name = 'DevSecOps'), 'prerequisite', 0.6),
    ((SELECT skill_id FROM skills WHERE name = 'Docker'), (SELECT skill_id FROM skills WHERE name = 'Kubernetes Security'), 'recommended_before', 0.5),
    ((SELECT skill_id FROM skills WHERE name = 'Cryptography'), (SELECT skill_id FROM skills WHERE name = 'Data Anonymization'), 'related_to', 0.3),
    ((SELECT skill_id FROM skills WHERE name = 'AWS'), (SELECT skill_id FROM skills WHERE name = 'Cloud Security'), 'recommended_before', 0.5),
    ((SELECT skill_id FROM skills WHERE name = 'NIST Cybersecurity Framework'), (SELECT skill_id FROM skills WHERE name = 'SOC 2 Compliance'), 'related_to', 0.6)
ON CONFLICT DO NOTHING;

-- =============================================================
-- External Mappings (LinkedIn, ESCO)
-- =============================================================

INSERT INTO skill_external_mappings (skill_id, external_system, external_id, external_name, mapping_type)
SELECT s.skill_id, 'linkedin', lower(s.name), s.name, 'exact'
FROM skills s
WHERE s.name IN ('Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes')
ON CONFLICT DO NOTHING;

-- =============================================================
-- Market Data (representative health scores)
-- =============================================================

INSERT INTO skill_market_data (skill_id, demand_score, growth_score, salary_median, competition_score, future_relevance, job_postings_count)
SELECT s.skill_id,
    CASE s.name
        WHEN 'Python' THEN 95 WHEN 'TypeScript' THEN 92 WHEN 'React' THEN 90
        WHEN 'Kubernetes' THEN 88 WHEN 'AWS' THEN 90 WHEN 'Docker' THEN 85
        WHEN 'Go' THEN 80 WHEN 'Rust' THEN 75 WHEN 'PyTorch' THEN 88
        WHEN 'TensorFlow' THEN 85 WHEN 'Prompt Engineering' THEN 95
        WHEN 'RAG (Retrieval-Augmented Generation)' THEN 90
        WHEN 'AI Agents' THEN 88 WHEN 'Transformers' THEN 82
        WHEN 'PostgreSQL' THEN 78 WHEN 'Terraform' THEN 82
        WHEN 'Application Security (AppSec)' THEN 80
        ELSE 70
    END,
    CASE s.name
        WHEN 'Python' THEN 25 WHEN 'TypeScript' THEN 20 WHEN 'Prompt Engineering' THEN 60
        WHEN 'RAG (Retrieval-Augmented Generation)' THEN 55 WHEN 'AI Agents' THEN 50
        WHEN 'Rust' THEN 35 WHEN 'Go' THEN 15 ELSE 10
    END,
    CASE s.name
        WHEN 'Python' THEN 120000 WHEN 'TypeScript' THEN 115000 WHEN 'React' THEN 110000
        WHEN 'Kubernetes' THEN 140000 WHEN 'AWS' THEN 130000 WHEN 'Go' THEN 125000
        WHEN 'Rust' THEN 135000 WHEN 'PyTorch' THEN 130000 WHEN 'TensorFlow' THEN 125000
        WHEN 'Application Security (AppSec)' THEN 135000
        WHEN 'Prompt Engineering' THEN 145000
        WHEN 'RAG (Retrieval-Augmented Generation)' THEN 140000
        ELSE 100000
    END,
    CASE s.name
        WHEN 'Python' THEN 40 WHEN 'JavaScript' THEN 60 WHEN 'React' THEN 55
        WHEN 'TypeScript' THEN 30 WHEN 'Rust' THEN 15 ELSE 35
    END,
    CASE s.name
        WHEN 'Python' THEN 95 WHEN 'Rust' THEN 85 WHEN 'PyTorch' THEN 90
        WHEN 'Prompt Engineering' THEN 88 WHEN 'RAG (Retrieval-Augmented Generation)' THEN 90
        WHEN 'AI Agents' THEN 85 ELSE 70
    END,
    CASE s.name
        WHEN 'Python' THEN 150000 WHEN 'TypeScript' THEN 80000 WHEN 'React' THEN 95000
        WHEN 'Kubernetes' THEN 45000 WHEN 'AWS' THEN 85000 ELSE 20000
    END
FROM skills s
WHERE s.name IN ('Python', 'TypeScript', 'React', 'Kubernetes', 'AWS', 'Docker', 'Go', 'Rust',
    'PyTorch', 'TensorFlow', 'Prompt Engineering', 'RAG (Retrieval-Augmented Generation)',
    'AI Agents', 'Transformers', 'PostgreSQL', 'Terraform', 'Application Security (AppSec)')
ON CONFLICT DO NOTHING;

COMMIT;
