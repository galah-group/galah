# The actual view
from galah.web import app
from flask import render_template, url_for
from collections import namedtuple

AsciiPiece = namedtuple("AsciiPiece", ["author", "art"])
ascii_art = {
    500: AsciiPiece(
        author = "pb", 
        art = """     __     __------           
  __/o `\ ,~   _~~  . ..   . ..
 ~ -.   ,'   _~-----           
     `\     ~~~--_'__          
       `~-==-~~~~~---          """        
    ),
    404: AsciiPiece(
        author = "Stephen Morgana",
        art = """             /\\              
              .\\\..          
              \\   \\         
              \ (o) /         
              (/    \         
               /\    \        
              ///     \       
             ///|     |       
            ////|     |       
           //////    /        
           |////    /         
          /|////--V/          
         //\//|   |           
     ___////__\___\__________ 
    ()_________'___'_________)"""
    )
}

messages = {
    500: """It appears something broke, I'm going to go fix it... In the meantime <a href="%s">Try Here</a>.""",
    404: """You seem to have landed in the wrong place... <a href="%s">Try Here</a>."""
}

@app.errorhandler(404)
@app.errorhandler(500)
def error(e):
    code = e.code if hasattr(e, "code") else 500
    
    if code == 500:
        error_description = "500: Internal Server Error"
    else:
        error_description = str(e)
    
    return render_template(
        "error.html",
        error_description = error_description,
        message = messages[code] % "/home", 
        art_piece = ascii_art[code]
    ), code
