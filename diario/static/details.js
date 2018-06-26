document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('novanota').addEventListener('click', function() {
        let header = document.getElementById('thead').children[0];
        let newEvent = document.createElement('td');
        newEvent.innerHTML = '<input type="text" name="description" placeholder="Avaliação">';
        header.insertBefore(newEvent, header.children[header.children.length-1]);

        let tbody = document.getElementById('tbody');
        for (let i = 0; i < tbody.children.length; ++i) {
            let tr = tbody.children[i];
            let studentId = tr.children[0].innerHTML;
            let td = document.createElement('td');
            td.innerHTML = '<input type="text" placeholder="Nota" name="student-' + studentId + '">';
            tr.insertBefore(td, tr.children[tr.children.length-1]);
        }
        
        let submit = document.getElementById('submitnotas');
        document.getElementById('novanota').classList.add('hidden');
        submit.classList.remove('hidden');
        submit.addEventListener('click', function() {
            submit.classList.add('hidden');
            document.getElementById('novanota').classList.remove('hidden');
        });
    });
});
