document.getElementById("event-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    fetch("/generate_event", {
        method: "POST",
        body: formData
    }).then((response) => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error("Failed to generate event.");
        }
    }).then((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "event.ics";
        a.click();
        URL.revokeObjectURL(url);
    }).catch((error) => {
        console.error("Error:", error);
        alert("Failed to generate event. Please try again.");
    });
});
