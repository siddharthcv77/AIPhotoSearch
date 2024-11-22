// Replace with your API Gateway URL and stage (e.g., 'prod')
const apiUrl = "https://dt275ym0yb.execute-api.us-east-1.amazonaws.com/prod2";

async function searchPhotos() {
    const query = document.getElementById("searchInput").value;
    try {
        const response = await fetch(`${apiUrl}/search?q=${query}`);
        const data = await response.json();
        displayResults(data.results);
    } catch (error) {
        console.error("Error searching photos:", error);
    }
}

function displayResults(results) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = ''; // Clear previous results

    // Replace 'your-bucket-name' with the actual name of your S3 bucket
    const bucketUrl = "https://b2-photo-storage.s3.amazonaws.com/";

    results.forEach(objectKey => {
        const img = document.createElement("img");
        img.src = `${bucketUrl}${objectKey}`;  // Construct the full URL
        img.alt = "Photo";
        img.className = "result-photo";
        resultsContainer.appendChild(img);
    });
}


async function uploadPhoto() {
    const fileInput = document.getElementById("fileInput");
    const customLabels = document.getElementById("customLabels").value;
    
    if (!fileInput.files[0]) {
        alert("Please select a file to upload.");
        return;
    }

    try {
        await fetch(`${apiUrl}/upload/${fileInput.files[0].name}`, {
            method: "PUT",
            headers: {
                "Content-Type": "image/jpeg",  // Ensure correct MIME type here
                "x-amz-meta-customLabels": customLabels,
            },
            body: fileInput.files[0],
        });        
        alert("Photo uploaded successfully!");
    } catch (error) {
        console.error("Error uploading photo:", error);
    }
}

