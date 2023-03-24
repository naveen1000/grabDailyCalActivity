echo "# myCalActivityLoad" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/naveen1000/myCalActivityLoad.git
git push -u origin main

npm init 
serverless.cmd deploy
serverless.cmd invoke -f myCalActivityLoad --log
#serverless.cmd deploy function --function myFunction

References:
https://www.serverless.com/framework/docs
https://github.com/serverless/github-action