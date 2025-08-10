import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# --- SAMPLE SPLUNK LOG DATA ---
EXCEPTIONS = [
    {
        "timestamp": datetime.now() - timedelta(minutes=5),
        "service": "payment-service",
        "exception": "NullPointerException at PaymentProcessor.java:45",
        "stack_trace": """java.lang.NullPointerException
    at com.fintech.payments.PaymentProcessor.process(PaymentProcessor.java:45)
    at com.fintech.api.PaymentAPI.handle(PaymentAPI.java:88)"""
    },
    {
        "timestamp": datetime.now() - timedelta(minutes=12),
        "service": "auth-service",
        "exception": "SQLTimeoutException at UserRepository.java:102",
        "stack_trace": """java.sql.SQLTimeoutException: Query timed out
    at com.fintech.db.UserRepository.findById(UserRepository.java:102)
    at com.fintech.api.AuthAPI.login(AuthAPI.java:54)"""
    }
]

# --- SAMPLE GITHUB CODE SNIPPETS ---
CODE_SNIPPETS = {
    "PaymentProcessor.java:45": """
public void process(Payment payment) {
    if (payment.getAccount() == null) {
        throw new NullPointerException();
    }
    // process payment
}
""",
    "UserRepository.java:102": """
public User findById(String id) {
    String query = "SELECT * FROM users WHERE id = ?";
    PreparedStatement stmt = connection.prepareStatement(query);
    stmt.setString(1, id);
    ResultSet rs = stmt.executeQuery();
    return mapToUser(rs);
}
"""
}

# --- MOCK RCA ANALYSIS ---
def analyze_exception(stack_trace):
    if "NullPointerException" in stack_trace:
        return {
            "root_cause": "Account object is null before processing payment.",
            "suggested_fix": "Add a null check and validation before calling process().",
            "related_commit": "Fix NPE in PaymentProcessor (#123)"
        }
    elif "SQLTimeoutException" in stack_trace:
        return {
            "root_cause": "Database query took too long due to missing index.",
            "suggested_fix": "Add an index on 'id' column in 'users' table.",
            "related_commit": "Optimize query for UserRepository (#98)"
        }
    else:
        return {
            "root_cause": "Unknown error.",
            "suggested_fix": "Investigate further.",
            "related_commit": None
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="RCA Dashboard", layout="wide")
st.title("🔍 Automated RCA Dashboard (Demo)")

# Sidebar - Log list
st.sidebar.header("📜 Exception Logs")
log_options = []
for idx, log in enumerate(EXCEPTIONS):
    log_options.append(f"{log['timestamp'].strftime('%H:%M:%S')} | {log['service']} | {log['exception']}")
selected_log = st.sidebar.radio("Select a log to analyze:", log_options)

# Find selected log data
log_index = log_options.index(selected_log)
log_data = EXCEPTIONS[log_index]

# Show Log Details
st.subheader("📌 Log Details")
st.json(log_data)

# Code Viewer
st.subheader("💻 Code Snippet")
file_line = log_data["exception"].split(" at ")[1] if " at " in log_data["exception"] else None
if file_line and file_line in CODE_SNIPPETS:
    st.code(CODE_SNIPPETS[file_line], language="java")
else:
    st.write("Code snippet not found.")

# RCA Analysis
st.subheader("🛠 Root Cause Analysis")
analysis = analyze_exception(log_data["stack_trace"])
st.write(f"**Root Cause:** {analysis['root_cause']}")
st.write(f"**Suggested Fix:** {analysis['suggested_fix']}")
if analysis["related_commit"]:
    st.write(f"**Related Commit:** {analysis['related_commit']}")

# Stack Trace
with st.expander("📄 Full Stack Trace"):
    st.code(log_data["stack_trace"], language="java")