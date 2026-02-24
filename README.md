# 🐾 Animal Rescue & Management System

A premium, comprehensive web application designed to streamline animal rescue operations, clinical management, and adoption workflows.

## 🚀 Key Features

### 🏛️ Role-Based Access Control
- **User**: Report rescues, track rescue status, and apply for pet adoption.
- **Rescue Team**: Receive alerts, respond to incidents, and transport animals to Care Centers.
- **Veterinarian**: Manage clinical records, prescribe treatments, and verify adoption readiness.
- **Care Center**: Manage resident animal logs, listing pets for adoption, and vetting applicant profiles.

### 🏥 Clinical & Management Suite
- **Recovery Tracking**: Dynamic progress bars and medical condition monitoring.
- **Pharmaceuticals & Nutrition**: Manage active therapeutic protocols and dietary requirements.
- **Case Chronology**: Detailed historical logs of clinical entries, diagnoses, and treatments.
- **Photo Management**: Care Centers can update animal photos for clear visibility.

### 🏠 End-to-End Adoption Workflow
- **Detailed Animal Files**: Potential adopters can review full clinical histories before requesting.
- **Request Management**: Users can track pending requests and cancel them if necessary.
- **Applicant Vetting**: Care Centers can view detailed profiles of applicants including contact information and residential details.
- **Decision Hub**: Efficient approval/rejection logic for Care Center staff.

## 🛠️ Technology Stack
- **Backend**: Django (Python)
- **Frontend**: Vanilla HTML5, CSS3, JavaScript
- **Styling**: Premium Glassmorphism UI, Responsive Design, HSL Color Palettes
- **Database**: SQLite (Development) / PostgreSQL (Production ready)

## 📦 Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/VishnuSuresh0204/Animal-Rescue.git
   ```

2. **Install dependencies**:
   ```bash
   pip install django pillow
   ```

3. **Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run the server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the app**:
   Open `http://127.0.0.1:8000/` in your browser.

## 🎨 Visual Identity
The system features a **Dark Theme Premium Aesthetic** with high-contrast typography and fluid micro-animations, ensuring an engaging experience for both professionals and community users.

---
*Developed for excellence in animal welfare and operational efficiency.*
