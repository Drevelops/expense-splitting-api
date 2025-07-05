# Expense Splitting API

A comprehensive FastAPI-based expense splitting application that helps groups efficiently split bills and track payments. Features advanced splitting algorithms, user management, and settlement optimization.

## 🚀 Features

- **Multiple Split Methods**: Equal splits, custom amounts, percentage-based, and income-ratio splitting
- **User Management**: Create and manage user profiles with email validation
- **Bill Management**: Create bills, add participants, and track payment status
- **Settlement Optimization**: Minimize the number of transactions needed to settle debts
- **RESTful API**: Clean, documented API endpoints with automatic validation
- **Database Relationships**: Robust PostgreSQL schema with proper foreign key constraints

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migration**: Alembic for database schema management
- **Authentication**: JWT-based authentication system
- **Documentation**: Automatic API documentation with Swagger UI
- **Validation**: Pydantic for request/response validation

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Drevelops/expense-splitting-api.git
   cd expense-splitting-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE expense_splitting;
   ```

5. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/expense_splitting
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Database Schema

### Users
- User profiles with name and email
- One-to-many relationship with created bills
- Many-to-many relationship with bill participation

### Bills
- Bill information with title and total amount
- Creator tracking and participant management
- One-to-many relationship with expenses

### Expenses
- Individual expense entries per participant
- Tracks amount owed and amount paid
- Supports different splitting methods

### Bill Participants (Association Table)
- Links users to bills they participate in
- Enables many-to-many relationships

## 🔀 Split Methods

1. **Equal Split**: Divides total amount equally among all participants
2. **Custom Amounts**: Allows manual assignment of specific amounts to each participant
3. **Percentage Split**: Splits based on custom percentages (must sum to 100%)
4. **Income Ratio**: Splits based on participants' income levels

## 📊 Settlement Algorithm

The API includes a debt optimization algorithm that:
- Calculates net balances for each participant
- Minimizes the number of transactions required
- Provides a clear settlement plan

## 🛣️ API Endpoints

### Users
- `POST /users/` - Create a new user
- `GET /users/{user_id}` - Get user details
- `GET /users/` - List all users

### Bills
- `POST /bills/` - Create a new bill
- `GET /bills/{bill_id}` - Get bill details
- `GET /bills/` - List user's bills
- `POST /bills/{bill_id}/participants` - Add participants to bill

### Expenses
- `GET /bills/{bill_id}/expenses` - Get all expenses for a bill
- `POST /bills/{bill_id}/split` - Calculate and create expense splits
- `PUT /expenses/{expense_id}/payment` - Record a payment

## 🚀 Deployment

### Using Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy with automatic PostgreSQL provisioning

### Using Docker
```bash
docker build -t expense-splitting-api .
docker run -p 8000:8000 expense-splitting-api
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

## 📖 Usage Examples

### Creating a Bill and Splitting Expenses

```python
# Create users
user1 = {"name": "Alice", "email": "alice@example.com"}
user2 = {"name": "Bob", "email": "bob@example.com"}

# Create a bill
bill = {
    "title": "Dinner at Restaurant",
    "total_amount": 120.00,
    "participants": [user1_id, user2_id, user3_id]
}

# Split equally
split_request = {
    "method": "equal"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Andre Wheeler**
- GitHub: [@Drevelops](https://github.com/Drevelops)
- Portfolio: [andre-wheeler.com](https://andre-wheeler.com)
- LinkedIn: [andre-wheeler](https://linkedin.com/in/andre-wheeler)

## 🔮 Future Enhancements

- [ ] Mobile app integration
- [ ] Receipt photo parsing with OCR
- [ ] Multi-currency support with real-time exchange rates
- [ ] Email notifications for payment reminders
- [ ] Integration with payment platforms (Venmo, PayPal)
- [ ] Expense categorization and analytics
- [ ] Group management and recurring bills