# Example Tasks for Testing Your Self-Learning AI Agent

Here are various example tasks you can use to test and demonstrate your self-learning AI agent's capabilities. These tasks range from simple to complex and showcase different aspects of the agent's learning abilities.

## 🎯 Simple Starter Tasks

These tasks help verify the basic functionality and establish initial experiences.

### 1. Basic Information Retrieval
```json
{
  "task": "What is the capital of France?",
  "context": { "session_id": "starter_1" }
}
```
**Learning Objective**: Establish basic fact retrieval pattern

### 2. Simple Calculation
```json
{
  "task": "Calculate 15% of 200",
  "context": { "session_id": "starter_2" }
}
```
**Learning Objective**: Establish mathematical reasoning pattern

### 3. Text Manipulation
```json
{
  "task": "Reverse the string 'hello world'",
  "context": { "session_id": "starter_3" }
}
```
**Learning Objective**: Establish string processing pattern

## 🔧 Intermediate Development Tasks

These tasks involve tool usage and more complex reasoning.

### 4. File Creation
```json
{
  "task": "Create a Python file named greet.py that prints 'Hello, Agent!' when executed",
  "context": { "session_id": "dev_1" }
}
```
**Tools Used**: Filesystem tool
**Learning Objective**: File creation and basic scripting

### 5. Web Search
```json
{
  "task": "Find the latest version of Python released in 2024",
  "context": { "session_id": "dev_2" }
}
```
**Tools Used**: Web search tool
**Learning Objective**: Information gathering and verification

### 6. Database Interaction
```json
{
  "task": "Create a simple SQLite database with a users table containing id, name, and email columns",
  "context": { "session_id": "dev_3" }
}
```
**Tools Used**: Database tool
**Learning Objective**: Database schema creation

### 7. Git Operations
```json
{
  "task": "Initialize a git repository and create a README.md file with basic project information",
  "context": { "session_id": "dev_4" }
}
```
**Tools Used**: Git tool
**Learning Objective**: Version control basics

## 🧠 Advanced Learning Tasks

These tasks demonstrate the agent's ability to learn from experience and improve over time.

### 8. Similar Task Recognition (After completing task 4)
```json
{
  "task": "Create a Python file named calculator.py that can add two numbers",
  "context": { "session_id": "learn_1" }
}
```
**Expected Improvement**: The agent should recognize similarity to task 4 and apply learned patterns

### 9. Progressive Complexity
```json
{
  "task": "Create a Python web scraper that extracts headlines from a news website",
  "context": { "session_id": "prog_1" }
}
```
**Learning Objective**: Complex tool chaining and error handling

### 10. Debugging and Fixing
```json
{
  "task": "Fix this broken Python code: print('Hello World'  # Missing closing parenthesis",
  "context": { "session_id": "debug_1" }
}
```
**Learning Objective**: Error detection and correction learning

## 📊 Data Analysis Tasks

### 11. Data Processing
```json
{
  "task": "Analyze this CSV data to find the average value in the 'price' column: name,price\\nApple,1.50\\nBanana,0.75\\nOrange,1.25",
  "context": { "session_id": "data_1" }
}
```
**Learning Objective**: Data parsing and statistical analysis

### 12. Visualization Request
```json
{
  "task": "Create a simple bar chart showing sales data: Q1: 100, Q2: 150, Q3: 200, Q4: 180",
  "context": { "session_id": "data_2" }
}
```
**Learning Objective**: Data visualization concepts

## 🤖 AI/ML Tasks

### 13. Prompt Engineering
```json
{
  "task": "Write a better prompt for getting an AI to explain quantum computing in simple terms",
  "context": { "session_id": "ai_1" }
}
```
**Learning Objective**: Meta-learning about AI interaction

### 14. Model Comparison
```json
{
  "task": "Compare the strengths and weaknesses of using rule-based systems vs machine learning for text classification",
  "context": { "session_id": "ai_2" }
}
```
**Learning Objective**: Comparative analysis and reasoning

## 🔄 Learning Demonstration Sequence

Run these tasks in sequence to clearly observe the learning improvement:

### Phase 1: Initial Experience (Tasks 15-17)
```json
[
  {
    "task": "Create a Python function that calculates factorial of a number",
    "context": { "session_id": "learn_seq_1" }
  },
  {
    "task": "Create a Python function that calculates fibonacci sequence up to n",
    "context": { "session_id": "learn_seq_2" }
  },
  {
    "task": "Create a Python function that checks if a number is prime",
    "context": { "session_id": "learn_seq_3" }
  }
]
```

### Phase 2: Similar Tasks (Tasks 18-20 - should show improvement)
```json
[
  {
    "task": "Create a Python function that calculates the sum of digits in a number",
    "context": { "session_id": "learn_seq_4" }
  },
  {
    "task": "Create a Python function that reverses a list without using built-in reverse",
    "context": { "session_id": "learn_seq_5" }
  },
  {
    "task": "Create a Python function that finds the maximum value in a list",
    "context": { "session_id": "learn_seq_6" }
  }
]
```

### Phase 3: Complex Application (Task 21 - should apply learned patterns)
```json
{
  "task": "Create a Python class that implements a simple calculator with add, subtract, multiply, divide methods",
  "context": { "session_id": "learn_seq_7" }
}
```

## 📈 Expected Learning Metrics Improvement

After running the learning sequence, you should observe:

1. **Decreased Execution Time**: Similar tasks execute faster
2. **Increased Success Rate**: Higher evaluation scores on similar tasks
3. **Reduced Tool Usage**: Agent reuses known patterns instead of exploring
4. **Better Strategy Selection**: More direct approaches to similar problems
5. **Experience Reuse**: Agent explicitly references past experiences in reasoning

## 🧪 Testing Commands

Use these curl commands to test the tasks:

```bash
# Simple task test
curl -X POST "http://localhost:8000/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "What is 25% of 80?", "context": {"session_id": "test_basic"}}'

# File creation test
curl -X POST "http://localhost:8000/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a file called test.txt with the content \"Learning is fun!\"", "context": {"session_id": "test_file"}}'

# Web search test
curl -X POST "http://localhost:8000/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Search for information about renewable energy trends in 2024", "context": {"session_id": "test_search"}}'

# Complex task test
curl -X POST "http://localhost:8000/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a REST API endpoint in Python that returns JSON user data", "context": {"session_id": "test_complex"}}'
```

## 💡 Tips for Best Learning Results

1. **Be Specific**: Clear, well-defined tasks lead to better learning
2. **Sequence Similar Tasks**: Run related tasks back-to-back to strengthen pattern recognition
3. **Vary Complexity**: Mix simple and complex tasks to build foundational then advanced skills
4. **Allow Mistakes**: The agent learns from failures too - don't only test tasks you know will succeed
5. **Review Experiences**: Use the memory endpoints to see what the agent has learned:
   ```bash
   curl "http://localhost:8000/api/memory/stats"
   curl "http://localhost:8000/api/agent/status"  # Contains learning stats
   ```

## 🎓 Educational Use Cases

These tasks work well for demonstrating AI learning concepts:

- **Pattern Recognition**: Show how the agent improves at similar tasks
- **Tool Chaining**: Demonstrate combining multiple tools for complex goals
- **Error Recovery**: Illustrate learning from failed attempts
- **Knowledge Transfer**: Display applying learned patterns to new domains
- **Meta-Learning**: Show the agent learning about its own learning process

**Remember**: The true power of a self-learning agent emerges over time as it builds a rich base of experiences to draw from. Start with these examples, then create your own tasks relevant to your domain or interests!