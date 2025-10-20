document.addEventListener('DOMContentLoaded', () => {

    const embedForm = document.getElementById('embed-form');
    const detectForm = document.getElementById('detect-form');
    const resultsArea = document.getElementById('results-area');
    const resultContent = document.getElementById('result-content');
    const loader = document.getElementById('loader');

    // --- ENHANCEMENT: Function to handle filename display ---
    function updateFileNameDisplay(inputElement, fileNameDisplayElement, fileName) {
        if (fileName) {
            fileNameDisplayElement.textContent = fileName;
            fileNameDisplayElement.classList.add('active');
        } else {
            fileNameDisplayElement.textContent = 'No file chosen';
            fileNameDisplayElement.classList.remove('active');
        }
    }

    // --- ENHANCEMENT: Setup Drag & Drop for both areas ---
    function setupDragAndDrop(dropArea, inputElement, fileNameDisplayElement) {
        // Highlight on drag over
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, e => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove('dragover');
            }, false);
        });

        // Handle the file drop
        dropArea.addEventListener('drop', e => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                inputElement.files = files;
                // Update the file name display
                updateFileNameDisplay(inputElement, fileNameDisplayElement, files[0].name);
            }
        }, false);
        
        // Also update filename when chosen via button
        inputElement.addEventListener('change', () => {
             if (inputElement.files.length > 0) {
                updateFileNameDisplay(inputElement, fileNameDisplayElement, inputElement.files[0].name);
            }
        });
    }

    // Initialize for Embed area
    setupDragAndDrop(
        document.getElementById('embed-drop-area'),
        document.getElementById('embed-audio'),
        document.getElementById('embed-file-name')
    );

    // Initialize for Detect area
    setupDragAndDrop(
        document.getElementById('detect-drop-area'),
        document.getElementById('detect-audio'),
        document.getElementById('detect-file-name')
    );


    // Function to show results and loader
    function showResult(isLoading, content = "") {
        resultsArea.style.display = 'block';
        if (isLoading) {
            loader.style.display = 'block';
            resultContent.innerHTML = '';
        } else {
            loader.style.display = 'none';
            resultContent.innerHTML = content;
        }
    }

    // Handle Embed form submission
    embedForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        showResult(true);

        const formData = new FormData(embedForm);

        try {
            const response = await fetch('/embed', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                const filename = data.download_filename;
                const downloadUrl = `/download/${filename}`;
                showResult(false, `<a href="${downloadUrl}" download>Download Sealed File (${filename})</a>`);
            } else {
                showResult(false, `<p class="error">Error: ${data.error}</p>`);
            }

        } catch (error) {
            showResult(false, `<p class="error">Server connection error: ${error.message}</p>`);
        }
    });

    // Handle Detect form submission
    detectForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        showResult(true);

        const formData = new FormData(detectForm);

        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                if (data.watermark === "[No Watermark Found]") {
                    showResult(false, `<p class="error">No watermark was found in this file.</p>`);
                } else {
                    showResult(false, `<p class="success">Secret Message Found: "${data.watermark}"</p>`);
                }
            } else {
                showResult(false, `<p class="error">Error: ${data.error}</p>`);
            }

        } catch (error) {
            showResult(false, `<p class="error">Server connection error: ${error.message}</p>`);
        }
    });

});

