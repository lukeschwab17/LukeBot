<h1>LukeBot</h1>
<h2>Multi-Purpose Discord Bot</h2>

Contains simple commands, embed/text games, and recording commands that are relevant to a seperate website project of mine.<br></br><br></br>


Notes: 
<ol>
  
  <li><h4>Part of this project is tied to my video website github project (https://github.com/lukeschwab17/LukeBot-Video-Website) Details:</li>
  <ul>
    <li>The website hosts videos created and automatically uploaded through discord servers (called 'guilds')</li>
    <ul>
      <li>Often, people want to capture moments (Playing a game, talking, etc) while with others online.</li>
      <li>Video clips are passed back and forth on servers, and this portion of the bot aims to categorize these videos and provide a place where they are easily searched for and watched online.</li>
      <li>Users can initialize a recording session, and any clips sent through text-chat during the session will be pushed into a compilation and uploaded to my created website.</li>
    </ul>
  </ul>
    <li><h4>While the video aspect is a substantial portion of the overall project, there are also games (text and media games), as well as general commands</li>
    <li><h4>in file_paths.py, you will see PROJECT_DIR. This is because I work in a larger directory that contains both projects, so it's useful for relative filepaths. </li>
    <li><h4>Finally, to update the project's database, I would like to have the bot listen for events such as users leaving and joining servers, but without 100% uptime (which will not happen from my home pc), that method would not work. Therefore, for now,
    the database table containing the bot's current discord servers' information is updated on any user command call.</li>
</ol>


<br></br><br></br>As per *help:

<h3>CoreCommands</h3><br></br>
  <b>al</b>: View all LukeBot saved avatars!<br></br>
  <b>avatar</b>: Change the bot avatar. Can use saved avatars, URL, or img file<br></br>
  <b>hello</b>: Hey there!<br></br>
  <b>wave</b>: Wave to someone!<br></br>
  <b>punch</b>: Punch someone!<br></br>
  <b>rtd</b>: Roll the dice.<br></br>
  <b>time</b>: Get the time in U.S. time zones.<br></br>
<h3>Media</h3><br></br>
  <b>gif</b>: Receive a random gif based on the prompt<br></br>
  <b>record_session</b>: Gathers and compiles clips into one while running<br></br>
  <b>videos</b>: View all LukeBot saved videos!<br></br>
  <b>wr</b>: Retrieve information about LoL players or champions.<br></br>
<h3>TextGames</h3><br></br>
  <b>picdle</b>: Guess cat or dog. Easy, Med, or Hard<br></br>
  <b>ttt</b>: Challenge another user to Tic-Tac-Toe<br></br>
  <b>typerace</b>: Create a TypeRacer lobby.<br></br>
  <b>wordle</b>: Create a wordle game.<br></br>
