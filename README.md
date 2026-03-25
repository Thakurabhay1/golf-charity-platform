# Golf Charity Subscription Platform

A subscription-based web application combining golf performance tracking, charity fundraising, and monthly prize draws.

## Features

- User registration and authentication
- Golf score tracking (Stableford format, 1-45)
- Monthly prize draws with 3-5 number matches
- Charity contribution system
- Admin dashboard for management
- Responsive web interface

## Setup

### Prerequisites

- Python 3.10+
- Supabase account (for database)
- Stripe account (for payments, optional for demo)

### Installation

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Supabase:
   - Create a new Supabase project
   - Run the SQL script in `sql_setup.sql` in the Supabase SQL editor
   - Get your project URL and anon key

5. Configure environment variables:
   - Copy `.env` and fill in your Supabase credentials
   - Add your JWT secret key
   - Add Stripe keys if implementing payments

6. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

7. Open http://127.0.0.1:8000 in your browser

## API Documentation

Once running, visit http://127.0.0.1:8000/docs for the interactive API documentation.

## Database Schema

The application uses the following main tables:
- `users`: User accounts and subscriptions
- `scores`: Golf scores (keeps last 5 per user)
- `charities`: Charity organizations
- `draws`: Monthly draw events
- `winners`: Draw winners and payouts

## Testing

Create a test admin user with email containing 'admin' (e.g., admin@example.com) to access admin features.

## Deployment

For production deployment:
- Set up a Supabase project
- Configure environment variables
- Deploy to Vercel or similar platform
- Set up proper domain and SSL