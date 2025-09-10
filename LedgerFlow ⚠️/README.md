# LedgerFlow - Professional Invoice Generator

A premium desktop application for generating highly realistic business invoices using imported Excel catalogs.

## ✨ New Features - Beginner Onboarding Flow

LedgerFlow now includes a comprehensive onboarding experience designed for new users:

### 🏠 Step-by-Step Onboarding
1. **Welcome Screen** - Personalized greeting with app statistics
2. **Company Information** - Collect business details for professional invoices
3. **Template Selection** - Choose from GST (India), Plain (Cash), or VAT (Bahrain) templates
4. **Excel Import** - Drag-and-drop interface for product catalog upload

### 🎨 Premium UI/UX
- **Glassmorphism Design** - Modern, professional interface with blur effects
- **Responsive Layout** - Works seamlessly on different screen sizes
- **Accessibility** - Full keyboard navigation and screen reader support
- **Dark/Light Theme** - Toggle between themes for comfortable viewing

### 🔧 Enhanced Dashboard
- **Quick Actions** - One-click access to common tasks
- **Real-time Statistics** - Live updates of invoices, products, and revenue
- **Smart Navigation** - Intuitive sidebar with clear section organization
- **Progress Tracking** - Visual indicators for multi-step processes

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Flask
- SQLite (included)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd LedgerFlow
```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Complete the onboarding flow for first-time users
   - Start generating professional invoices!

## 📋 Features

### Invoice Templates
- **GST Invoice (India)** - Supports item-wise mixed GST rates (5%, 12%, 18%, 28%)
- **Plain Invoice (Cash)** - Simple invoices for local businesses
- **VAT Invoice (Bahrain)** - Compliant with 0% and 10% VAT rates

### Advanced Generation
- **Realism Controls** - Adjust realism level and believability stress
- **Customer Patterns** - Configurable customer repeat rates
- **Business Styles** - Multiple business type simulations
- **Statistical Distribution** - Realistic invoice patterns

### Import & Export
- **Excel Import** - Drag-and-drop product catalog upload
- **PDF Export** - Professional invoice PDFs
- **Excel Export** - Data export for analysis
- **Template Download** - Pre-formatted Excel templates

### Security & Compliance
- **Passcode Protection** - Secure access control
- **Audit Logging** - Complete activity tracking
- **Data Integrity** - Tamper detection and verification
- **Session Management** - Secure user sessions

## 🎯 Use Cases

### Small Business Owners
- Generate professional invoices quickly
- Maintain consistent branding
- Track customer patterns
- Export data for accounting

### Accountants & Bookkeepers
- Bulk invoice generation
- Multiple business support
- Tax compliance features
- Data export capabilities

### Developers & Testers
- Realistic test data generation
- Invoice simulation for testing
- Pattern analysis tools
- Export functionality

## 🔧 Configuration

### Business Settings
- Company name and address
- GST/VAT numbers
- Contact information
- Invoice numbering format

### Generation Parameters
- Realism level (0-100%)
- Stress level for anomalies
- Customer repeat density
- Business style selection

### Export Options
- PDF page size and format
- Excel color coding
- ZIP folder structure
- Watermark settings

## 📊 Dashboard Features

### Real-time Statistics
- Total invoices generated
- Products imported
- Revenue calculations
- Category breakdowns

### Quick Actions
- Import products
- Generate invoices
- Manual entry
- Export data

### Recent Activity
- Latest imports
- Recent generations
- Export history
- System notifications

## 🛡️ Security Features

### Access Control
- Passcode authentication
- Session timeout
- IP logging
- Brute force protection

### Data Protection
- Encrypted settings
- Audit trail
- Integrity checks
- Secure file handling

## 🎨 UI/UX Highlights

### Modern Design
- Glassmorphism effects
- Smooth animations
- Responsive layout
- Professional color scheme

### Accessibility
- Keyboard navigation
- Screen reader support
- High contrast options
- Focus indicators

### User Experience
- Intuitive onboarding
- Clear progress indicators
- Helpful tooltips
- Error handling

## 📈 Performance

### Optimization
- Efficient database queries
- Lazy loading
- Cached templates
- Background processing

### Scalability
- Modular architecture
- Configurable settings
- Extensible templates
- Plugin support

## 🔄 Development

### Code Structure
```
LedgerFlow/
├── app/
│   ├── core/           # Core business logic
│   ├── models/         # Database models
│   ├── services/       # Business services
│   ├── static/         # Frontend assets
│   ├── templates/      # HTML templates
│   └── utils/          # Utility functions
├── config.py           # Configuration
├── app.py             # Main application
└── requirements.txt   # Dependencies
```

### Key Components
- **Crystal Core** - Advanced invoice generation engine
- **VeriChain** - Data integrity verification
- **Security Manager** - Access control and audit
- **Diagnostics Logger** - System monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Open an issue on GitHub
- Contact the development team

---

**LedgerFlow** - Professional invoice generation made simple and beautiful. 