#Web Game Catalog version 1.00  01/13/2016

README
------
- Web Game Catalog, is a Web database of Video Games. It allows you to Creae,Read,Update and Delete Game data on the Database. 
- Web Game Catalog accepts the following pieces of information about a Game:
  - Game Name 
  - Game Description/Synopsis
  - Price 
  - Consoles the Game is avaiable on.
  - Genre 
  - Age Rating

----------------------------------------------------------------------------

SETUP NOTES
-----------
1. Install Vagrant and VirtualBox if you have not done so already. Instructions on how to do so can be found on the websites as well as in the course materials..
2. Clone the fullstack-nanodegree-vm repository. There is a catalog folder provided for you, but no files have been included. If a catalog folder does not exist, simply create your own inside of the vagrant folder.
3. Launch the Vagrant VM (by typing vagrant up in the directory fullstack/vagrant from the terminal). You can find further instructions on how to do so here.
4. Write the Flask application locally in the /vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM). Name it application.py.
5. Run your application within the VM by typing python /vagrant/catalog/application.py into the Terminal. If you named the file from step 4 as something other than application.py, in the above command substitute in the file name on your computer.
6. Access and test your application by visiting http://localhost:8000 locally on your browser.

GENERAL USAGE NOTES
-------------------

Add a Game
-----------
- On the Home Page, click Add Game
- If you are not logged in you will be prompeted to log In.
- You can use your Facebook or Google accounts to Log in. 
- Add the Need Game info.
	- For the Image link copy any web image url for the game and paste it in the textbox.
- Click Create to Add the Game
- Game will now show on the home page.

Add a Console
-------------
- Click Add Console
- You will be prompted to Log In if you aren't already.
- Once on the Add Console Page
- Type a Name of a Console
- Click Create 


Add a Genre
-----------
- Click Add Genre
- You will be prompted to Log In if you aren't already.
- Once on the Add Genre Page
- Type a Name of a Genre
- Click Create

View a Game Details
-------------------
- Click on the Game title in the Home page 
- This will take you to the Game Details page


View a Games by Console
-----------------------
- Click Consoles in the Side bar
- Select the Console you are looking for in the Drop Down Menu
- Click Select to see all the Games avaibale on the Console

View a Games by Genre
-----------------------
- Click Genres in the Side bar
- Select the Genre you are looking for in the Drop Down Menu
- Click Select to see all the Games avaibale in the Genre


Edit a Game
-----------
- First Log in 
- Click on the Game title in the Home page 
- This will take you to the Game Details page
- If the game belongs to you meaning, you created it.
- Then the Edit Game Button will appear click it to Edit the Game



Delete a Game
-------------
- First Log in 
- Click on the Game title in the Home page 
- This will take you to the Game Details page
- If the game belongs to you meaning, you created it.
- Then the Delete Game Button will appear click it to Delete the Game







===========================================================================
