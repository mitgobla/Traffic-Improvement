var updateButton = document.getElementById('updateButton');
var examsCardDeck = document.getElementById('examsCardDeck');
var examBoardSelect = document.getElementById('examBoardSelect');
var levelSelect = document.getElementById('levelSelect');
var subjectSelect = document.getElementById('subjectSelect');

var get_selected_sections = function () {
    console.log({ examBoard: $("#examBoardSelect :selected").val(), level: $("#levelSelect :selected").val(), subject: $("#subjectSelect :selected").val() })
    return { examBoard: $("#examBoardSelect :selected").val(), level: $("#levelSelect :selected").val(), subject: $("#subjectSelect :selected").val() };
};

update_filters = function () {
    $.post("update-filters", get_selected_sections(), function (data, status) {
        var filterObject = JSON.parse(data);
        // Exam Board Select Update
        examBoardsArray = filterObject['examBoards'];
        for (examBoardIndex in examBoardsArray) {
            examBoard = examBoardsArray[examBoardIndex];
            if (!$('#examBoardSelect option[value="' + examBoard + '"]').prop("selected", true).length) {
                selectElement = document.createElement('option');
                selectElement.appendChild(document.createTextNode(examBoard));
                selectElement.setAttribute('value', examBoard);
                examBoardSelect.appendChild(selectElement);
            };
        };
        // Level Select Update
        levelsArray = filterObject['levels'];
        for (levelIndex in levelsArray) {
            level = levelsArray[levelIndex];
            if (!$('#levelSelect option[value="' + level + '"]').prop("selected", true).length) {
                selectElement = document.createElement('option');
                selectElement.appendChild(document.createTextNode(level));
                selectElement.setAttribute('value', level);
                levelSelect.appendChild(selectElement);
            };
        };
        // Subject Select Update
        subjectsArray = filterObject['subjects'];
        for (subjectIndex in subjectsArray) {
            subject = subjectsArray[subjectIndex];
            selectElement = document.createElement('option');
            selectElement.appendChild(document.createTextNode(subject));
            selectElement.setAttribute('value', subject);
            subjectSelect.appendChild(selectElement);
        };
    });
};

update_exams = function () {
    $.post("get-exams", get_selected_sections(), function (data, status) {
        var examArray = JSON.parse(data);
        while (examsCardDeck.firstChild) {
            examsCardDeck.removeChild(examsCardDeck.firstChild)
        }
        for (exam in examArray) {
            var examObject = examArray[exam];
            // console.log(typeof(examObject))
            // var examListItem = document.createElement('li');
            // console.log(Object.keys(examObject));
            // examListItem.appendChild(document.createTextNode(examObject['level']));
            // examList.appendChild(examListItem);
            var examCard = document.createElement('div');
            examCard.classList.add('card')
            var examCardBody = document.createElement('div');
            examCardBody.classList.add('card-body');
            var examCardLevel = document.createElement('h5');
            examCardLevel.appendChild(document.createTextNode(examObject.level))
            var examCardSubject = document.createElement('h6');
            examCardSubject.appendChild(document.createTextNode(examObject.subject))
            examCardBody.appendChild(examCardLevel);
            examCardBody.appendChild(examCardSubject);
            examCard.appendChild(examCardBody);
            examsCardDeck.appendChild(examCard);

        };
    });
};

$(document).on('change', '#examBoardSelect', function () {
    update_exams();
});

$(document).on('change', '#levelSelect', function () {
    update_exams();
});

$(document).on('change', '#subjectSelect', function () {
    update_exams();
});

update_filters()