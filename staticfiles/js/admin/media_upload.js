(function($) {
    $(document).ready(function() {
        // Target the media form more reliably
        if (!$('body.app-cms.model-media').length) return;
        
        // Create the dropzone element
        const $fileField = $('.field-file input[type="file"]');
        if (!$fileField.length) return;
        
        const $dropzone = $('<div class="dropzone"><div class="icon">📁</div><p>Drag & drop files here</p><p>or</p><button type="button" class="button">Select Files</button></div>');
        const $progressContainer = $('<div class="upload-progress"><div class="progress"><div class="progress-bar" role="progressbar"></div></div><div class="upload-list"></div></div>');
        
        // Insert the dropzone after the file field
        $fileField.parent().append($dropzone);
        $dropzone.after($progressContainer);
        
        // Hide the original file field label
        $fileField.parent().find('label').hide();
        
        // Hide the original file field
        $fileField.hide();
        
        // Handle click on the select files button
        $dropzone.find('button').on('click', function() {
            // Create a new file input
            const $newFileInput = $('<input type="file" multiple style="display:none">');
            $('body').append($newFileInput);
            
            // Trigger click on the new file input
            $newFileInput.trigger('click');
            
            // Handle file selection
            $newFileInput.on('change', function() {
                handleFiles(this.files);
                // Remove the temporary file input
                $newFileInput.remove();
            });
        });
        
        // Handle drag and drop events
        $dropzone.on('dragenter dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $dropzone.addClass('highlight');
        });
        
        $dropzone.on('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $dropzone.removeClass('highlight');
        });
        
        $dropzone.on('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $dropzone.removeClass('highlight');
            
            const dt = e.originalEvent.dataTransfer;
            const files = dt.files;
            
            handleFiles(files);
        });
        
        // Function to handle the selected files
        function handleFiles(files) {
            if (files.length === 0) return;
            
            // Show the progress container
            $progressContainer.show();
            
            // Process each file
            Array.from(files).forEach(file => {
                uploadFile(file);
            });
        }
        
        // Function to upload a file
        function uploadFile(file) {
            // Create a new form data
            const formData = new FormData();
            formData.append('file', file);
            formData.append('title', file.name.split('.')[0].replace(/[_-]/g, ' '));
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            formData.append('csrfmiddlewaretoken', csrfToken);
            
            // Create a new upload item
            const $uploadItem = $('<div class="upload-item"><div class="upload-name">' + file.name + '</div><div class="upload-status">Uploading...</div></div>');
            $progressContainer.find('.upload-list').append($uploadItem);
            
            // If it's an image, create a preview
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    $uploadItem.prepend('<img src="' + e.target.result + '" alt="' + file.name + '">');
                };
                reader.readAsDataURL(file);
            }
            
            // Send the AJAX request
            $.ajax({
                url: '/cms/admin/cms/media/upload/',  // Updated URL to match your project structure
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                xhr: function() {
                    const xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener('progress', function(e) {
                        if (e.lengthComputable) {
                            const percent = Math.round((e.loaded / e.total) * 100);
                            $progressContainer.find('.progress-bar').css('width', percent + '%');
                        }
                    }, false);
                    return xhr;
                },
                success: function(response) {
                    console.log('Upload successful:', response);
                    $uploadItem.find('.upload-status').text('Uploaded').addClass('success');
                    // Refresh the page after a short delay to show the new media
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                },
                error: function(xhr, status, error) {
                    console.error('Upload error:', xhr.responseText);
                    $uploadItem.find('.upload-status').text('Error: ' + error).addClass('error');
                }
            });
        }
    });
})(django.jQuery);