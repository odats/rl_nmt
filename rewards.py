import unicodedata


def count_uppercase_letters(text):
    return sum(1 for char in text if char.isupper())

# # Example usage:
# text = "Hello World! THIS is a TEST."
# print(f"The number of uppercase letters is: {count_uppercase_letters(text)}")

# text = "Привіт Я, Test."
# print(f"The number of uppercase letters is: {count_uppercase_letters(text)}")


def count_non_letters_no_spaces(text):
    # count = 0
    # for char in text:
    #     if not unicodedata.category(char).startswith('L') and not char.isspace():
    #         count += 1
    # return count

    return len(get_non_letters_no_spaces(text))

# # Example usage:
# text = "Hello, 世界! 123 Привіт!  😊"
# count = count_non_letters_no_spaces(text)
# print(f"Number of non-letter characters: {count}")

# text = "Hello, 世界! 123 Приввіт!,  😊"
# count = count_non_letters_no_spaces(text)
# print(f"Number of non-letter characters: {count}")


# def get_non_letters_no_spaces(text):
#     tokens = []
#     for char in text:
#         if not unicodedata.category(char).startswith('L') and not char.isspace():
#             tokens.append(char)
#     return tokens

def get_non_letters_no_spaces(text):
    preserved = set("0123456789()[]{}.:;!?-+=*/%<>$€₴£¥") # removed ,
    return [char for char in text if char in preserved]

# # Example usage:
# text1 = "Hello, 世界! 123 Привіт!  😊"
# tokens1= get_non_letters_no_spaces(text1)
# print(tokens1)


# text2 = "Привіт, 世界7 123 Привіт!  😊"
# tokens2= get_non_letters_no_spaces(text2)
# print(tokens2)


def count_unpaired_items(list1, list2):
    list2_copy = list2.copy()  # avoid modifying the original list2
    unmatched_list1 = []

    for c in list1:
        if c in list2_copy:
            list2_copy.remove(c)  # remove one matching item
        else:
            unmatched_list1.append(c)  # item from list1 has no pair

    #print(unmatched_list1, list2_copy)

    return len(unmatched_list1) + len(list2_copy)


def count_words(text):
    if not text.strip():
        return 0
    
    # Split the text into words (handling multiple spaces and line breaks)
    words = text.split()
    
    return len(words)

# # Example usage:
# sample_text = """
# This is a sample text   with several words.    
# It includes punctuation, line breaks, and   multiple   spaces.
# """

# word_count = count_words(sample_text)
# print(f"Total words: {word_count}")


def count_unique_words(text):
    # Split text into words by whitespace
    words = text.lower().split()
    unique_words = set(words)
    return len(unique_words)

# # Example usage
# text = "This is a test. This test is simple!"
# print("Unique word count:", count_unique_words(text))


# def relative_difference(a, b):
#     return 1 - (abs(a - b) / (a + b + 1e-9))

def relative_difference(a, b):
    min_val = 1e-3  # More reasonable minimum
    a_adj = max(a, min_val)
    b_adj = max(b, min_val)
    return 1 - (abs(a_adj - b_adj) / (a_adj + b_adj))


# print(relative_difference(1,0))
# print(relative_difference(2,1))

# Rewards

# same number of uppercase letters: A,Z,Г,... 
def reward_count_uppercase_letters(completions, sources, references = None, **kwargs):
    rewards = []
    for src, comp in zip(sources, completions):
        src_count = count_uppercase_letters(src)
        comp_count = count_uppercase_letters(comp)

        rewards.append(relative_difference(src_count, comp_count))

    return rewards

# same number of special characters: 1,2,?,!,(...
def reward_count_non_letters_no_spaces(completions, sources, references = None, **kwargs):
    rewards = []
    for src, comp in zip(sources, completions):
        src_count = count_non_letters_no_spaces(src)
        comp_count = count_non_letters_no_spaces(comp)

        rewards.append(relative_difference(src_count, comp_count))

    return rewards

# same number of words: hello, world, how, are, you
def reward_count_words(completions, sources, references = None, **kwargs):
    rewards = []
    for src, comp in zip(sources, completions):
        src_count = count_words(src)
        comp_count = count_words(comp)

        rewards.append(relative_difference(src_count, comp_count))

    return rewards

# same number of unique words: source= "Hello. How are you", translation = "Привіт. Привіт Привіт Привіт."
def reward_count_unique_words(completions, sources, references = None, **kwargs):
    rewards = []
    for src, comp in zip(sources, completions):
        src_count = count_unique_words(src)
        comp_count = count_unique_words(comp)

        rewards.append(relative_difference(src_count, comp_count))

    return rewards

# same special characters: souce = "1 2 3", # translation = "* * *"
def reward_count_unpaired_items(completions, sources, references = None, **kwargs):
    rewards = []
    for src, comp in zip(sources, completions):
        src_tokens = get_non_letters_no_spaces(src)
        comp_tokens = get_non_letters_no_spaces(comp)

        unmatched = count_unpaired_items(src_tokens, comp_tokens)
        total = len(src_tokens) + len(comp_tokens) + 1e-9
        count_normalized = 1 - (unmatched / total)

        rewards.append(count_normalized)

    return rewards


# ---------------------------------------------------------------------------------------------
# Lixical

# pip install spacy
# python -m spacy download uk_core_news_lg 
# python -m spacy download en_core_web_lg

import spacy

# Load English language model
nlp_en = spacy.load("en_core_web_lg")
nlp_ukr = spacy.load("uk_core_news_lg")

def count_nouns_verbs_adjectives(nlp, text):
    doc = nlp(text)
    mapping = {
        "PROPN": "NOUN",  # proper nouns
    }

    counts = {
        "NOUN": 0,  # іменники
        "VERB": 0,  # дієслова
        "ADJ": 0    # прикметники
    }
    for token in doc:
        pos = mapping.get(token.pos_, token.pos_)
        if pos in counts:
            counts[pos] += 1
    return counts

def reward_lexical(completions, sources, references = None, **kwargs):
    rewards = []
    for sentence_en, sentence_uk in zip(sources, completions):  
        counts_en = count_nouns_verbs_adjectives(nlp_en, sentence_en)
        counts_uk = count_nouns_verbs_adjectives(nlp_ukr, sentence_uk)

        reward_nouns = relative_difference(counts_en['NOUN'], counts_uk['NOUN'])
        reward_verb = relative_difference(counts_en['VERB'], counts_uk['VERB']) 
        reward_adj = relative_difference(counts_en['ADJ'], counts_uk['ADJ'])

        reward = (reward_nouns + reward_verb + reward_adj) / 3

        rewards.append(reward)

    return rewards

# sentence_en = "The quick brown fox jumps over the lazy dog and runs away."
# counts_en = count_nouns_verbs_adjectives(nlp_en, sentence_en)
# print(counts_en)

# sentence_uk = "Швидкий рудий лис стрибає через ледачого пса і."
# counts_uk = count_nouns_verbs_adjectives(nlp_ukr, sentence_uk)
# print(counts_uk)

# reward_lexical([sentence_uk], [sentence_en])