let currentIndex = 0;
const carousel = document.querySelector('.carousel');
const cards = document.querySelectorAll('.card1');
const totalCards = cards.length;
const dotsContainer = document.querySelector('.dots-container');

// Function to calculate card width including margin
function getCrdWidth() {
  return cards[0].offsetWidth + 31; // width + margin of 15px
}
function getCardWidth() {
  const card = cards[0];

  const style = window.getComputedStyle(card);
  const marginRight = parseFloat(style.marginRight);
  const marginLeft = parseFloat(style.marginLeft);

  return card.offsetWidth + marginLeft + marginRight;
}
// Create Dots
function createDots() {
  for (let i = 0; i < totalCards; i++) {
    const dot = document.createElement('span');
    dot.classList.add('dot');
    dot.onclick = () => {
      currentIndex = i;
      moveSlide();
    };
    dotsContainer.appendChild(dot);
  }
  updateDots();
}

// Move to the next slide
function moveSlide() {
  const cardWidth = getCardWidth(); // Dynamically calculate card width

  // Infinite loop: move to the first card when we reach the last one
  if (currentIndex >= totalCards) {
    currentIndex = 0; // Loop back to the first slide
    carousel.style.transition = 'none'; // Disable transition for instant reset
    carousel.style.transform = `translateX(0px)`; // Jump to the first card
    setTimeout(() => {
      carousel.style.transition = 'transform 0.5s ease-in-out'; // Re-enable transition
      moveSlide(); // Continue sliding to the next slide
    }, 50); // Wait for the reset to take effect
  } else if (currentIndex < 0) {
    currentIndex = totalCards - 1; // Go to the last slide if going backward
  } else {
    carousel.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
  }
  updateDots();
}

// Update Dots
function updateDots() {
  const dots = document.querySelectorAll('.dot');
  dots.forEach((dot, index) => {
    dot.classList.remove('active');
    if (index === currentIndex) {
      dot.classList.add('active');
    }
  });
}

// Auto-Slide every 3 seconds
let autoSlideInterval = setInterval(() => {
  currentIndex++;
  moveSlide();
}, 2000);

// Pause auto-slide on hover
document.querySelector('.carousel-container').addEventListener('mouseenter', () => {
  clearInterval(autoSlideInterval);
});

// Restart auto-slide on mouse leave
document.querySelector('.carousel-container').addEventListener('mouseleave', () => {
  autoSlideInterval = setInterval(() => {
    currentIndex++;
    moveSlide();
  }, 2000);
});

// Resize listener to update card width
window.addEventListener('resize', () => {
  moveSlide();
});

// Initialize the carousel
createDots();
moveSlide(); // Set the initial slide

function myFunction1() {
  var input, filter, table, tr, td, i, j, txtValue, found;

  input = document.getElementById('myInput');
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");

  // start from 1 to skip header (th)
  for (i = 1; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td");
    found = false;

    for (j = 0; j < td.length; j++) {
      txtValue = td[j].textContent || td[j].innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        found = true;
        break;
      }
    }

    tr[i].style.display = found ? "" : "none";
  }
}

/// Function to filter table rows based on input and show the table when the user types
function myFunction() {
var input, filter, table, tr, td, i, txtValue;
input = document.getElementById('myInput');
filter = input.value.toUpperCase();
table = document.getElementById("myTable");
tr = table.getElementsByTagName("tr");
//document.write(input,filter,table,tr)
// Show the table when the user starts typing
if (input.value.length > 0) {
  table.style.display = "table"; // Show table when user starts typing
} 
else {
  table.style.display = "none"; // Hide table if input is empty
}

// Loop through all table rows, starting from 1 (to skip the header row)
for (i = 0; i < tr.length; i++) {
  td = tr[i].getElementsByTagName("td")[0]; // Check the name column

  if (td) {
    txtValue = td.textContent || td.innerText;

    // If the name matches the filter, display the row, else hide it
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      tr[i].style.display = "";
    } else {
      tr[i].style.display = "none";
    }
  }
}
}

function toggleSidebar() {
const sidebar = document.getElementById('sidebar');
sidebar.classList.toggle('expanded');}



setTimeout(() => {
    document.querySelectorAll('.flash-message')
        .forEach(msg => msg.remove());
}, 3000);



