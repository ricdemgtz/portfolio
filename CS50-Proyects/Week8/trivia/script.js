document.addEventListener('DOMContentLoaded', () => {

    // --- DATA: Pool of 20 Questions ---
    const allQuestions = [
        // Multiple Choice Questions
        { type: 'mc', question: 'What is the largest mammal in the world?', answers: [{ text: 'Elephant', correct: false }, { text: 'Blue Whale', correct: true }, { text: 'Giraffe', correct: false }, { text: 'Great White Shark', correct: false }] },
        { type: 'mc', question: 'Which planet has the most moons?', answers: [{ text: 'Jupiter', correct: false }, { text: 'Saturn', correct: true }, { text: 'Earth', correct: false }, { text: 'Mars', correct: false }] },
        { type: 'mc', question: 'What is the chemical symbol for gold?', answers: [{ text: 'Ag', correct: false }, { text: 'Go', correct: false }, { text: 'Au', correct: true }, { text: 'Gd', correct: false }] },
        { type: 'mc', question: 'Who wrote "Romeo and Juliet"?', answers: [{ text: 'Charles Dickens', correct: false }, { text: 'Jane Austen', correct: false }, { text: 'William Shakespeare', correct: true }, { text: 'Mark Twain', correct: false }] },
        { type: 'mc', question: 'What is the main ingredient in guacamole?', answers: [{ text: 'Tomato', correct: false }, { text: 'Avocado', correct: true }, { text: 'Onion', correct: false }, { text: 'Lime', correct: false }] },
        { type: 'mc', question: 'How many continents are there?', answers: [{ text: '5', correct: false }, { text: '6', correct: false }, { text: '7', correct: true }, { text: '8', correct: false }] },
        { type: 'mc', question: 'What is the capital of Canada?', answers: [{ text: 'Toronto', correct: false }, { text: 'Vancouver', correct: false }, { text: 'Montreal', correct: false }, { text: 'Ottawa', correct: true }] },
        { type: 'mc', question: 'In which year did the Titanic sink?', answers: [{ text: '1905', correct: false }, { text: '1912', correct: true }, { text: '1918', correct: false }, { text: '1923', correct: false }] },
        { type: 'mc', question: 'What is the hardest natural substance on Earth?', answers: [{ text: 'Gold', correct: false }, { text: 'Iron', correct: false }, { text: 'Diamond', correct: true }, { text: 'Quartz', correct: false }] },
        { type: 'mc', question: 'Which artist painted the Mona Lisa?', answers: [{ text: 'Vincent van Gogh', correct: false }, { text: 'Pablo Picasso', correct: false }, { text: 'Leonardo da Vinci', correct: true }, { text: 'Michelangelo', correct: false }] },

        // Free Response Questions
        { type: 'fr', question: 'Which country is known as the Land of the Rising Sun?', correctAnswer: 'japan' },
        { type: 'fr', question: 'What is the name of the galaxy that contains our Solar System?', correctAnswer: 'milky way' },
        { type: 'fr', question: 'What is the capital city of Australia?', correctAnswer: 'canberra' },
        { type: 'fr', question: 'How many sides does a hexagon have?', correctAnswer: '6' },
        { type: 'fr', question: 'What gas do plants absorb from the atmosphere?', correctAnswer: 'carbon dioxide' },
        { type: 'fr', question: 'Who was the first person to walk on the moon?', correctAnswer: 'neil armstrong' },
        { type: 'fr', question: 'What is the longest river in the world?', correctAnswer: 'nile' },
        { type: 'fr', question: 'What is the currency of the United Kingdom?', correctAnswer: 'pound' },
        { type: 'fr', question: 'What is H2O more commonly known as?', correctAnswer: 'water' },
        { type: 'fr', question: 'What is the largest ocean on Earth?', correctAnswer: 'pacific' }
    ];

    // --- DOM Elements ---
    const quizArea = document.getElementById('quiz-area');
    const questionText = document.getElementById('question-text');
    const answerOptions = document.getElementById('answer-options');
    const feedbackText = document.getElementById('feedback-text');
    const endScreen = document.getElementById('end-screen');
    const restartButton = document.getElementById('restart-button');

    // --- Game State ---
    let availableQuestions = [];

    // --- Functions ---
    function startGame() {
        // Make a copy of all questions to draw from
        availableQuestions = [...allQuestions];
        endScreen.classList.add('hidden');
        quizArea.classList.remove('hidden');
        loadNextQuestion();
    }

    function loadNextQuestion() {
        // If no questions are left, end the game
        if (availableQuestions.length === 0) {
            endGame();
            return;
        }

        // Clear previous state
        feedbackText.textContent = '';
        answerOptions.innerHTML = '';

        // Get a random question
        const questionIndex = Math.floor(Math.random() * availableQuestions.length);
        const currentQuestion = availableQuestions[questionIndex];

        // Remove the question from the available pool to avoid repeats
        availableQuestions.splice(questionIndex, 1);

        // Display the question
        displayQuestion(currentQuestion);
    }

    function displayQuestion(question) {
        questionText.textContent = question.question;

        if (question.type === 'mc') {
            // Create buttons for multiple choice
            question.answers.forEach(answer => {
                const button = document.createElement('button');
                button.textContent = answer.text;
                button.addEventListener('click', (e) => handleAnswer(answer.correct, e.target));
                answerOptions.appendChild(button);
            });
        } else if (question.type === 'fr') {
            // Create input and a confirmation button for free response
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'fr-input';

            const submitButton = document.createElement('button');
            submitButton.textContent = 'Confirm Answer';
            submitButton.addEventListener('click', () => {
                const userAnswer = input.value.toLowerCase().trim();
                const isCorrect = userAnswer === question.correctAnswer;
                handleAnswer(isCorrect, input);
            });

            answerOptions.appendChild(input);
            answerOptions.appendChild(submitButton);
        }
    }

    function handleAnswer(isCorrect, element) {
        // Disable all buttons to prevent multiple clicks
        const allButtons = answerOptions.querySelectorAll('button');
        allButtons.forEach(button => button.disabled = true);

        const originalColor = element.style.backgroundColor;
        const originalTextColor = element.style.color;

        if (isCorrect) {
            element.style.backgroundColor = 'green';
            element.style.color = 'white';
            feedbackText.textContent = 'Correct!';
            feedbackText.style.color = 'green';

            // After a delay, load the next question
            setTimeout(() => {
                loadNextQuestion();
            }, 1500); // 1.5-second delay

        } else {
            element.style.backgroundColor = 'red';
            element.style.color = 'white';
            feedbackText.textContent = 'Incorrect! Try again.';
            feedbackText.style.color = 'red';

            // After a delay, reset the question for another try
            setTimeout(() => {
                element.style.backgroundColor = originalColor;
                element.style.color = originalTextColor;
                feedbackText.textContent = '';
                // Re-enable buttons for another attempt
                allButtons.forEach(button => button.disabled = false);
            }, 2000); // 2-second delay
        }
    }

    function endGame() {
        quizArea.classList.add('hidden');
        endScreen.classList.remove('hidden');
    }

    // --- Event Listeners ---
    restartButton.addEventListener('click', startGame);

    // --- Initial Call ---
    startGame();
});
