ZeroFiles (.zr) - a way better version of JSON
So basically, I got tired of how annoying JSON is (why can't we just use comments??), so I made my own file format called ZeroFiles (.zr). It's super lightweight and way easier to read. It basically takes the easy stuff from JS objects and YAML, but adds cool stuff like header metadata and comments that actually stay there when you format it.

I coded the whole thing from scratch in Python—like the lexer, parser, AST generator, formatter, and even a linter. No external libraries or anything, just pure code.

Cool Features
Actual Comments: You can use #, //, or even /* block comments */. Finally.

Comments Don't Disappear: My formatter uses a custom AST, so when it cleans up your code, it doesn't just delete your comments like other annoying parsers do.

Headers: You can put special tags at the very top of the file using # @key: value.

No Annoying Quotes: You don't have to put quotes around object keys anymore if they're just normal names. It looks super clean, kinda like JavaScript.

Built-in Linter: It catches stuff like using single quotes when you shouldn't, and if you mess up the syntax, it tells you the exact line and column number so you can fix it fast.

What a .zr file looks like:
Python
# @version: 1.0
# @author: Dev
# @project: Global Configuration

{
    // Server data
    server: {
        host: "127.0.0.1",
        port: 8080, /* Default port */
        debug_mode: true
    },
    
    # List of administrators
    admins: [
        "admin_user",
        "root"
    ]
}

Made for HackClub / Stardance
