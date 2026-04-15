const imageInputs = document.getElementsByName('image');
const previewImages = document.querySelectorAll('.image-preview');
[...imageInputs].forEach((imageInput, i) => {

imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let previewImage = previewImages[i]
            if (!previewImage) {
                previewImage = document.createElement('img');
                previewImage.id = 'image-preview';
                previewImage.width = 250;
                previewImage.height = "auto";
                previewImage.alt = 'product image preview';
                imageInput.parentNode.appendChild(previewImage);
            }
            previewImage.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

});


// const imageInput = document.getElementById('id_image');

// imageInput.addEventListener('change', function(event) {
//     const file = event.target.files[0];
//     if (file) {
//         const reader = new FileReader();
//         reader.onload = function(e) {
//             let previewImage = document.getElementById('image-preview');
//             if (!previewImage) {
//                 previewImage = document.createElement('img');
//                 previewImage.id = 'image-preview';
//                 previewImage.width = 250;
//                 previewImage.height = 250;
//                 previewImage.alt = 'product image preview';
//                 imageInput.parentNode.appendChild(previewImage);
//             }
//             previewImage.src = e.target.result;
//         };
//         reader.readAsDataURL(file);
//     }
// });