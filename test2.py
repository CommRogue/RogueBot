Directory = "C:\\Users\\guyst\\Desktop\\alice.txt"

def getWord(word): #takes a word, makes it lowercase,
                    # and removes non-english characters
                    #from the first and last characters.
                    #(words like "it's" will not have
                    #their special characters removed.
    word = list(word.lower())
    removedCharacters = False
    while not removedCharacters and len(word) > 0: #loop runs until all special characters are
                                 #removed from the start
        if not (97 <= ord(word[0]) <= 122):  # if the first character is not
            word.pop(0)                      # a lowercase english character
        else:
            removedCharacters = True

    removedCharacters = False
    while not removedCharacters and len(word) > 0:#loop runs until all special characters are
                                 #removed from the start
        if not (97 <= ord(word[len(word)-1]) <= 122): #checking the last character
            word.pop(len(word)-1)                     # a lowercase english character
        else:
            removedCharacters = True

    return ''.join(word)

def getMatches(text): #function takes in text as string, and returns an array
                      #that represents the number of times each word appeared in it.

    words = {} #this represents the dictionary of words.
               #the key is the word itself, and the value is the number of words.

    text_split = text.split() #represents the text variable splitted into an array
    for word in text_split:
        word = getWord(word)
        if word != "":
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
    return words

def printResult(words, text): #function takes in an array of the number of words,
                              #and the text from the document. prints the result.
    print("----Program Start-----")
    print("**Your input - **")
    print(text)
    print("\n**Number of words: **")
    for word in words:
        print('- Word "'+word+'": appeared '+str(words[word])+' times.')

def main(): #main function
    file = open(Directory, 'r')
    text = file.read() #represents the string representation of the file
    if text == "":
        print("You did not input anything in the text file.")
    else:
        word_count = getMatches(text)
        printResult(word_count, text)

main()