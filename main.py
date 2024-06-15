from st_pages import Page, show_pages, add_page_title

# Optional -- adds the title and icon to the current page
add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("main.py", "Home", "🏠"),
        Page("register.py", "Membership", "🔼"),
        Page("cal.py", "PT Plan", ":books:"),
        Page("app_f.py", "Video List & Plan", "👏"),
        Page("calendar1.py", "Calendar", "📅"),
    ]
)