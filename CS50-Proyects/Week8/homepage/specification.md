# Specification for My Homepage Project

## 10+ HTML Tags Used

1.  **nav**: To create the main navigation bar section.
2.  **a**: For hyperlinks to navigate between pages and for branding.
3.  **ul**: To create an unordered list for navigation items.
4.  **li**: For each individual item in the navigation list.
5.  **main**: To define the main content area of each page.
6.  **div**: As a general container for layout, used extensively with Bootstrap's grid and components.
7.  **h1, h2, h5**: For various levels of headings to structure content.
8.  **p**: For paragraphs of text.
9.  **button**: For interactive elements like the "Fun Fact" button and form submission.
10. **footer**: To define the footer section of each page.
11. **img**: To display images in the hobbies and gallery pages.
12. **form**: To create the contact form.
13. **input**: For text and email entry fields in the form.
14. **textarea**: For the multi-line message field in the form.
15. **script**: To include Bootstrap's JavaScript and my own custom scripts.

## 5+ CSS Properties and Selectors

### Selectors

-   **Tag Selector**: `body`, `footer`
-   **Class Selector**: `.navbar-custom`, `.card`
-   **ID Selector**: `#fun-fact-button`
-   **Pseudo-class Selector**: `:hover` (used on `.card:hover`)
-   **Descendant Selector**: (Implicitly used, e.g., styling elements within `.jumbotron`)

### Properties

-   **background-color**: Used for the body, navbar, and footer.
-   **font-family**: Set a base font for the entire site in the body.
-   **box-shadow**: Added to the navbar and cards on hover for a depth effect.
-   **transition**: Used on cards to animate the hover effect smoothly.
-   **transform**: Used with `scale()` to enlarge cards on hover.
-   **font-size**: Used in the footer to make the text slightly smaller.
-   **color**: Used to define text color in various elements.

## JavaScript and Bootstrap Usage

-   **Bootstrap**: I used Bootstrap's responsive navbar, jumbotron, grid system (rows/columns), and cards to structure the layout and ensure the site looks good on all devices.
-   **JavaScript**: I used JavaScript to add interactivity by making a "Fun Fact" button on the homepage reveal hidden text and by showing a confirmation message when the contact form is submitted.
