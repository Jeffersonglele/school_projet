FROM python:3.11-slim

# Met a jour apt et installe les dependances systemes requises pour le pilote ODBC
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Ajoute la cle et le depot Microsoft pour Debian 12 (bookworm)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
RUN curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Installe le pilote ODBC 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Definit le dossier de travail
WORKDIR /app

# Copie et installe les dependances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code
COPY . .

# Expose le port (Render injecte la variable PORT, mais 10000 est une bonne valeur par defaut)
EXPOSE 10000

# Lance l'application avec uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
