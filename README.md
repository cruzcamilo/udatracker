# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

# Short reflection

I have previous experience with native Android development using Kotlin, and a few years ago, I worked with Java to create REST APIs. Although I have used Python before, I hadn't used it for building APIs, so much of the syntax in this exercise was new to me.

I implemented the code with the help of AI. I believe TDD is highly relevant nowadays; as code generation becomes easier and cheaper, it is even more important to establish boundaries and expected results through tests. However, I still consider it crucial to be able to read and understand generated code. Since people will eventually need to maintain and debug it, clarity must remain a priority.

If I were to continue with the project, adding persistent storage would be a great next step.