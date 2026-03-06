const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
    mode: "python",
    theme: "material-darker",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autofocus: true,
});

const taskIdInput = document.getElementById("task-id");
const tokenInput = document.getElementById("auth-token");
const stdinInput = document.getElementById("stdin");
const outputPanel = document.getElementById("output-panel");
const statusBadge = document.getElementById("api-status");
const statusMessage = document.getElementById("api-message");
const lastAction = document.getElementById("last-action");
const testResultsBody = document.querySelector("#test-results-table tbody");

function updateStatus(action, state, message) {
    lastAction.textContent = action;
    statusBadge.textContent = state;
    statusBadge.className = "badge " + (state === "success" ? "text-bg-success" : state === "error" ? "text-bg-danger" : "text-bg-warning");
    statusMessage.textContent = message;
}

function getAuthHeaders() {
    const token = tokenInput.value.trim();
    if (!token) {
        throw new Error("Auth token is required. Please paste token from /login or /register.");
    }
    const normalizedToken = token.startsWith("Token ") ? token : `Token ${token}`;
    return {
        "Content-Type": "application/json",
        Authorization: normalizedToken,
    };
}

function renderSubmissionResult(submission) {
    testResultsBody.innerHTML = "";
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${submission.id ?? "-"}</td>
        <td>${submission.status ?? "-"}</td>
        <td>${submission.passed_tests ?? 0}</td>
        <td>${submission.total_tests ?? 0}</td>
        <td>${submission.score ?? 0}</td>
    `;
    testResultsBody.appendChild(row);
}

async function runCode() {
    const sourceCode = editor.getValue();
    const taskId = taskIdInput.value ? Number(taskIdInput.value) : undefined;

    try {
        updateStatus("Run code", "pending", "Sending code to runner API...");
        const response = await fetch("/run-code", {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                task_id: taskId,
                source_code: sourceCode,
                stdin: stdinInput.value,
            }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || JSON.stringify(data));
        }

        outputPanel.textContent = [
            `Status: ${data.status || "queued"}`,
            `Message: ${data.message || "Code submitted."}`,
            data.preview ? `Preview: ${data.preview}` : "",
            data.stdout ? `\nSTDOUT:\n${data.stdout}` : "",
            data.stderr ? `\nSTDERR:\n${data.stderr}` : "",
        ].filter(Boolean).join("\n");

        updateStatus("Run code", "success", data.message || "Code execution request queued.");
    } catch (error) {
        outputPanel.textContent = `Error: ${error.message}`;
        updateStatus("Run code", "error", error.message);
    }
}

async function submitSolution() {
    const sourceCode = editor.getValue();
    const taskId = Number(taskIdInput.value);

    if (!taskId) {
        updateStatus("Submit solution", "error", "Task ID is required for submission.");
        return;
    }

    try {
        updateStatus("Submit solution", "pending", "Submitting solution...");
        const response = await fetch("/submit-solution", {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                task_id: taskId,
                source_code: sourceCode,
                language: "python",
            }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || JSON.stringify(data));
        }

        const submission = data.submission || {};
        renderSubmissionResult(submission);

        outputPanel.textContent = [
            data.message || "Submitted.",
            `Submission #${submission.id ?? "-"}`,
            `Status: ${submission.status ?? "queued"}`,
            `Passed tests: ${submission.passed_tests ?? 0}/${submission.total_tests ?? 0}`,
            `Score: ${submission.score ?? 0}`,
        ].join("\n");

        updateStatus("Submit solution", "success", data.message || "Solution submitted.");
    } catch (error) {
        outputPanel.textContent = `Error: ${error.message}`;
        updateStatus("Submit solution", "error", error.message);
    }
}

document.getElementById("run-btn").addEventListener("click", runCode);
document.getElementById("submit-btn").addEventListener("click", submitSolution);
document.getElementById("clear-output-btn").addEventListener("click", () => {
    outputPanel.textContent = "Output cleared.";
    testResultsBody.innerHTML = '<tr><td colspan="5" class="text-muted">No test results yet.</td></tr>';
    updateStatus("Clear output", "pending", "Output and test table reset.");
});
