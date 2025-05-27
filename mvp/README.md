# MVP Streamlit Interfaces

This directory contains the MVP (Minimum Viable Product) Streamlit interfaces for the Virtual Client project.

## Quick Start

### Prerequisites

1. **Environment Variables**: The project uses a `.env` file for configuration.
   - Copy `.env.example` to `.env` if you haven't already
   - The API key should be set in the `.env` file
   - The project automatically loads environment variables from `.env`

2. **Database**: Ensure the database is initialized:
   ```bash
   python backend/scripts/init_db_orm.py
   ```

3. **Dependencies**: Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Applications

1. **Teacher Test Interface**:
   ```bash
   streamlit run mvp/teacher_test.py
   ```
   - Create and manage virtual clients
   - Test conversations with clients
   - View conversation history and metrics

2. **Student Practice Interface** (coming soon):
   ```bash
   streamlit run mvp/student_practice.py
   ```

3. **Admin Monitor** (coming soon):
   ```bash
   streamlit run mvp/admin_monitor.py
   ```

## Environment Variables

- `ANTHROPIC_API_KEY`: Required for AI conversations
- `APP_ENV`: Set to "development" (default) or "production"
- `ANTHROPIC_MODEL`: Override default model selection (optional)

## Testing Without Valid API Key

If you're experiencing API authentication issues:

1. **Check API Key Validity**:
   ```bash
   python check_api_key.py
   ```

2. **Create Mock Conversations** (for UI testing):
   ```bash
   python create_mock_conversation.py
   ```

3. **Use Fallback Mode**: The system will automatically use mock responses when API authentication fails, allowing you to test the UI flow.

## Features Implemented

### Part 1: MVP Setup ✅
- Basic infrastructure and utilities
- Mock authentication for testing
- Database connection helpers

### Part 2: Teacher Interface - Client Form ✅
- Create virtual clients with detailed profiles
- Save clients to database
- View and manage existing clients

### Part 3: Teacher Interface - Test Conversation ✅
- Start conversations with virtual clients
- Real-time chat interface
- Token counting and cost tracking
- End conversation functionality

### Upcoming Features

- Part 4: Teacher Interface - Metrics & History
- Part 5: Student Interface - Client Selection
- Part 6: Student Interface - Conversation
- Part 7: Admin Dashboard - Basic Metrics
- Part 8: Admin Dashboard - Enhanced Monitoring

## Testing Without API Key

The system will show appropriate error messages if no API key is configured. To run tests:

```bash
# Run all tests (some will be skipped without API key)
python run_tests.py

# Run only UI logic tests (no API key required)
python run_tests.py tests/integration/test_teacher_interface_integration.py::TestConversationUILogic
```

## Cost Information

- **Development/Testing**: Uses Claude 3 Haiku (~$0.003 per conversation)
- **Production**: Uses Claude 3 Sonnet (~$0.03 per conversation)
- Cost tracking is built-in with configurable alerts

## Troubleshooting

1. **"Invalid API Key" or 401 Authentication errors**:
   - Verify your API key is valid: `python check_api_key.py`
   - Ensure the key in `.env` has no extra spaces or quotes
   - The system will use mock responses for testing when authentication fails

2. **"Anthropic API key not configured" error**:
   - Make sure `.env` file exists in project root
   - Check that `ANTHROPIC_API_KEY=your-key-here` is in the file
   - Restart the Streamlit app after adding the key

3. **Database connection errors**:
   - Ensure the database is initialized: `python backend/scripts/init_db_orm.py`
   - Check that the virtual environment is activated

4. **Import errors**:
   - Make sure you're running from the project root directory
   - Verify all dependencies are installed: `pip install -r requirements.txt`

5. **AttributeError with session_service**:
   - This has been fixed in the latest version
   - Make sure you have the latest code
