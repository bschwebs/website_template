#!/usr/bin/env python3
"""
Database Initialization Script for Flask Story Publishing Website
This script creates the SQLite database and optionally populates it with sample data.
"""

import sqlite3
import os
from datetime import datetime

DATABASE = 'content.db'

def create_database():
    """Create the SQLite database and tables."""
    print("Creating database and tables...")
    
    # Remove existing database if it exists
    if os.path.exists(DATABASE):
        response = input(f"Database '{DATABASE}' already exists. Do you want to recreate it? (y/N): ")
        if response.lower() != 'y':
            print("Database initialization cancelled.")
            return False
        os.remove(DATABASE)
        print(f"Removed existing database: {DATABASE}")
    
    # Create new database connection
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create posts table
    cursor.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            image_filename TEXT,
            post_type TEXT NOT NULL DEFAULT 'article',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_post_type ON posts(post_type)')
    cursor.execute('CREATE INDEX idx_created_at ON posts(created_at DESC)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database '{DATABASE}' created successfully!")
    return True

def populate_sample_data():
    """Add sample stories and articles to the database."""
    print("\nAdding sample data...")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    sample_posts = [
        # Sample Stories
        {
            'title': 'The Last Library',
            'content': '''In the year 2087, books were nothing more than relics of a forgotten past. The Great Purge of 2045 had seen to that, when the Global Council declared physical books "inefficient vessels of knowledge" and mandated their destruction.

But Elena had a secret.

Hidden beneath the ruins of what was once the New York Public Library, she maintained the last collection of physical books on Earth. Each night, she would descend through a concealed entrance, past layers of rubble and decay, into a sanctuary that glowed with the warm light of oil lamps.

The underground chamber housed over ten thousand books, carefully preserved in climate-controlled cases that Elena had built herself. Philosophy, poetry, fiction, history – the entire breadth of human thought and imagination lived on in these pages.

Tonight was different, though. Elena had detected unusual electromagnetic signatures near the surface. The Council's enforcement drones were getting closer. She had perhaps hours before they found her sanctuary.

As she ran her fingers along the spines of centuries-old books, Elena made a decision that would change everything. She activated the emergency protocol she had hoped never to use – a network of hidden caches and trusted allies who would ensure that human knowledge would survive, even if she didn't.

The last library would not fall in silence.''',
            'excerpt': 'In a world where books are forbidden, one librarian holds the key to humanity\'s past.',
            'post_type': 'story'
        },
        {
            'title': 'The Time Merchant',
            'content': '''Marcus Chen had always been good at finding things that others had lost. Lost keys, lost pets, lost hope – he had a knack for restoration. But when he inherited his grandfather's antique shop in San Francisco's Chinatown, he discovered something far more extraordinary.

Hidden behind a false wall in the basement, Marcus found a room filled with hourglasses of every size and description. Some were made of crystal that seemed to pulse with inner light, others of metals that shouldn't exist, and a few of what appeared to be crystallized starlight.

Each hourglass contained time itself – not just sand, but moments, memories, and possibilities. A note in his grandfather's handwriting explained the impossible truth: their family had been Time Merchants for over three centuries, trading in the most precious commodity of all.

The rules were simple but absolute: Never sell your own time. Never trade a moment that would create a paradox. And never, ever, let the Council of Temporal Guardians discover your existence.

Marcus thought he understood, until Mrs. Patterson walked into his shop on a rainy Tuesday morning, clutching a photograph of her late husband and asking if he could sell her just one more day with him.

Standing in that dimly lit shop, surrounded by the gentle tick of a thousand timepieces, Marcus realized that being a Time Merchant wasn't about understanding time – it was about understanding the weight of every precious second that slips through our fingers like sand.''',
            'excerpt': 'When Marcus inherits his grandfather\'s shop, he discovers a family business dealing in time itself.',
            'post_type': 'story'
        },
        
        # Sample Articles
        {
            'title': 'The Art of Creative Writing: Finding Your Voice',
            'content': '''Every writer begins with the same question: "How do I find my voice?" It's a question that has launched a thousand writing workshops and filled countless notebooks with experimental prose. But the truth about finding your voice as a writer might surprise you.

Your voice isn't something you discover – it's something you develop.

**Understanding Voice vs. Style**

Many new writers confuse voice with style. Style is the technical aspect of your writing: your sentence structure, word choice, and rhythm. Voice, on the other hand, is your unique perspective on the world, the way you see and interpret experiences that makes your writing distinctly yours.

Think of voice as your literary fingerprint. Just as no two people have identical fingerprints, no two writers should have identical voices. Your voice emerges from your background, your experiences, your worldview, and yes, even your struggles.

**The Development Process**

Finding your voice is less about discovery and more about refinement. Here's how to approach it:

1. **Read Voraciously**: Expose yourself to different authors, genres, and time periods. Notice what resonates with you and what doesn't. Pay attention to how different writers approach similar themes.

2. **Write Regularly**: Your voice develops through practice. Write in different genres, experiment with different perspectives, and don't be afraid to imitate writers you admire – it's part of the learning process.

3. **Embrace Your Uniqueness**: Your background, culture, and personal experiences are your greatest assets as a writer. Don't try to sound like someone else; the world already has one of them.

4. **Be Patient**: Voice development is a marathon, not a sprint. Some writers find their voice quickly, others take years. Both paths are valid.

**Common Pitfalls to Avoid**

The biggest mistake new writers make is trying to force a voice that isn't authentic to them. This often happens when writers try to imitate successful authors too closely or when they think they need to sound "literary" to be taken seriously.

Another common issue is switching voices mid-story or even mid-paragraph. Consistency is key to developing a strong, recognizable voice.

**Practical Exercises**

Try these exercises to help develop your voice:

- Write the same scene from three different perspectives
- Describe your childhood home in exactly 100 words
- Write a letter to your teenage self
- Reimagine a fairy tale in your own words

**The Bottom Line**

Your voice as a writer is already inside you – it just needs time and practice to emerge fully. Be patient with yourself, write consistently, and remember that every published author started exactly where you are now: with a blank page and a story to tell.

The world needs your unique perspective. Trust in your voice, even when it's still finding its way.''',
            'excerpt': 'Exploring the fundamental techniques and mindset needed to develop your unique writing voice.',
            'post_type': 'article'
        },
        {
            'title': 'Building Compelling Characters: Beyond the Surface',
            'content': '''Character development is the heart of great storytelling. Readers don't fall in love with plots – they fall in love with characters. They don't stay up until 3 AM reading because they need to know what happens next; they stay up because they need to know what happens to the people they've grown to care about.

But creating compelling characters goes far beyond physical descriptions and personality traits. It requires understanding the deeper psychology of human nature and translating that understanding into fictional beings that feel real.

**The Iceberg Principle**

Hemingway's iceberg theory applies perfectly to character development. What readers see on the page – your character's actions, dialogue, and immediate thoughts – represents only the tip of the iceberg. The vast majority of who your character is lies beneath the surface: their history, their fears, their unconscious motivations, and their deepest desires.

This doesn't mean you need to write a 50-page biography for every character, but you should know them well enough that their actions feel inevitable rather than arbitrary.

**Core Elements of Character Development**

**Motivation and Desire**: Every compelling character wants something, and that want drives their actions throughout the story. But the best characters want multiple things that often conflict with each other. A character might want security but also crave adventure, or desire love while fearing vulnerability.

**Internal Conflict**: External conflict drives plot, but internal conflict drives character development. The most interesting characters are fighting battles within themselves – struggling with their past, questioning their beliefs, or wrestling with difficult decisions.

**Change and Growth**: Static characters, no matter how well-drawn initially, become boring over time. Characters need to change, learn, and grow throughout your story. This doesn't mean they need to become completely different people, but they should be somehow transformed by their experiences.

**Flaws and Contradictions**: Perfect characters are perfectly boring. Real people are bundles of contradictions, and your characters should be too. The brave hero who's afraid of spiders, the wise mentor who makes terrible personal decisions, the villain who genuinely loves their cat – these contradictions make characters feel human.

**Techniques for Character Development**

**The Character Interview**: Sit down and interview your characters as if they were real people. Ask them about their childhood, their fears, their proudest moments, and their biggest regrets. You'll be surprised by what you discover.

**Backstory Exercises**: Write scenes from your character's past that will never appear in your story. How did they handle their first heartbreak? What was their relationship with their parents like? These exercises help you understand how your character became who they are.

**Reaction Tests**: Put your character in various hypothetical situations and consider how they would react. How would they handle a flat tire? A surprise party? A moral dilemma? Consistent reactions help establish personality.

**Dialogue Practice**: Write conversations between your characters about mundane topics. How they discuss the weather or their lunch plans can reveal as much about their personality as their reactions to major plot events.

**Show, Don't Tell Character Traits**

Instead of telling readers that your character is generous, show them giving their umbrella to a stranger in the rain. Instead of stating that someone is anxious, show them checking the locks on their door three times before bed.

Actions, dialogue, and small details are far more powerful than adjectives when it comes to revealing character.

**The Role of Supporting Characters**

Your supporting characters aren't just plot devices – they're opportunities to reveal different facets of your protagonist. How your main character interacts with their best friend, their enemy, their parent, and a stranger on the street should all feel different and reveal different aspects of their personality.

**Avoiding Character Clichés**

Be aware of character archetypes and stereotypes, but don't avoid them entirely. Instead, find ways to subvert expectations. Take a familiar character type and give them an unexpected trait, motivation, or background that makes them fresh.

**The Long Game**

Character development is a long-term investment. The characters you create today will grow and evolve not just within their current story, but potentially across multiple works. Some of literature's most beloved characters feel like real people because their creators spent years understanding and developing them.

Remember, readers can sense when a character is fully realized versus when they're just a collection of traits. Invest the time in truly knowing your characters, and your readers will thank you by caring about their journey as much as you do.''',
            'excerpt': 'A deep dive into creating characters that readers will remember long after finishing your story.',
            'post_type': 'article'
        },
        {
            'title': 'The Power of Setting: Creating Worlds That Live and Breathe',
            'content': '''Setting is far more than just a backdrop for your story – it's a character in its own right, capable of influencing mood, driving conflict, and revealing deeper truths about your characters and themes. The best settings don't just house your story; they actively participate in it.

**Beyond Geography: Understanding True Setting**

When most writers think about setting, they focus on the physical: the time period, the location, the weather. While these elements are important, true setting encompasses much more. It includes the social atmosphere, the economic conditions, the cultural norms, and the emotional landscape of your story world.

Consider how different your story would feel if set in a small farming town during the Great Depression versus a bustling tech startup in modern San Francisco. The change isn't just visual – it affects everything from your characters' speech patterns to their deepest fears and greatest aspirations.

**Setting as Character**

The most memorable settings have personality. They have moods, they change over time, and they affect the people who inhabit them. Think about how the isolated hotel in "The Shining" becomes increasingly malevolent, or how the post-apocalyptic wasteland in "The Road" reflects the internal desolation of its characters.

Your setting should have:
- **Atmosphere**: The emotional tone that permeates the environment
- **History**: Past events that have shaped the physical and social landscape  
- **Rules**: Both natural laws and social conventions that govern how things work
- **Secrets**: Hidden aspects that can be revealed over time

**Research and Authenticity**

Whether you're writing about a real place or creating a fictional world, research is crucial. This doesn't mean you need to become an expert on every detail, but you should understand enough to write with confidence and authenticity.

For real locations, consider:
- Geography and climate
- Local customs and dialect
- Historical events that shaped the area
- Economic conditions and social structures
- Current issues and conflicts

For fictional worlds, you still need internal consistency. Your fantasy realm or science fiction future should follow logical rules that you've established.

**Sensory Details: Bringing Setting to Life**

The key to vivid setting is engaging all five senses, not just sight. What does your setting smell like? What sounds fill the air? What textures would your characters feel? How might the air taste after a storm or in a smoky bar?

These sensory details should serve the story, not overwhelm it. Choose details that:
- Advance the plot or reveal character
- Establish or enhance mood
- Make the setting feel lived-in and real
- Support your story's themes

**Setting and Pacing**

Your setting descriptions should match your story's pacing. During action scenes, brief, sharp details work best. During quieter, more reflective moments, you can afford longer, more detailed descriptions.

Learn to weave setting details throughout your narrative rather than front-loading them in large blocks of description. A few well-chosen details scattered through a scene are often more effective than a paragraph of pure description.

**Cultural and Social Setting**

Don't forget the social landscape of your story. The cultural norms, class structures, and social expectations of your setting can create as much conflict as any physical obstacle. A character's struggle against societal expectations can be just as compelling as their battle against a natural disaster.

Consider how your setting's social rules affect:
- How characters interact with each other
- What conflicts are possible or likely
- What your characters can and cannot do
- How they speak and behave

**Setting as Theme**

Your setting can reinforce your story's themes in powerful ways. A story about isolation might be set on a remote island or in a crowded city where the protagonist feels alone. A tale about renewal could unfold during spring or in a place rebuilding after destruction.

The key is subtlety – let the setting support your themes without hitting readers over the head with obvious symbolism.

**Practical Tips for Setting Development**

1. **Create a setting bible**: Keep track of important details about your world to maintain consistency
2. **Use maps and floor plans**: Visual aids help you keep spatial relationships clear
3. **Visit or study similar real places**: Even fantasy settings benefit from real-world inspiration
4. **Interview locals**: If writing about a real place you haven't visited, talk to people who have lived there
5. **Consider seasonal changes**: How does your setting change throughout the year?

**Common Setting Mistakes to Avoid**

- **Info-dumping**: Overwhelming readers with too much setting information at once
- **Generic descriptions**: Using clichéd or overly familiar imagery
- **Inconsistency**: Changing details about your setting mid-story
- **Irrelevance**: Including setting details that don't serve the story
- **Stereotype reliance**: Depending on cultural or geographic stereotypes instead of research

**The Emotional Landscape**

Remember that setting isn't just about physical space – it's about emotional space too. How does your setting make your characters feel? How does it make your readers feel? The emotional resonance of your setting can be just as important as its physical details.

A well-crafted setting becomes inseparable from the story itself. Readers should feel like they've visited your world, breathed its air, and understood its rhythms. When setting is done well, readers will miss it when the story ends – and that's the mark of a truly successful fictional world.''',
            'excerpt': 'How to create immersive story worlds that enhance plot, character, and theme.',
            'post_type': 'article'
        }
    ]
    
    # Insert sample posts
    for post in sample_posts:
        cursor.execute('''
            INSERT INTO posts (title, content, excerpt, post_type)
            VALUES (?, ?, ?, ?)
        ''', (post['title'], post['content'], post['excerpt'], post['post_type']))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {len(sample_posts)} sample posts to the database!")

def display_database_info():
    """Display information about the created database."""
    print(f"\n📊 Database Information:")
    print(f"Database file: {DATABASE}")
    print(f"Location: {os.path.abspath(DATABASE)}")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Count total posts
    cursor.execute('SELECT COUNT(*) FROM posts')
    total_posts = cursor.fetchone()[0]
    
    # Count by type
    cursor.execute('SELECT post_type, COUNT(*) FROM posts GROUP BY post_type')
    post_counts = cursor.fetchall()
    
    print(f"Total posts: {total_posts}")
    for post_type, count in post_counts:
        print(f"  {post_type.title()}s: {count}")
    
    conn.close()

def create_directories():
    """Create necessary directories for the Flask app."""
    directories = ['templates', 'static', 'static/uploads']
    
    print("\nCreating directory structure...")
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def main():
    """Main function to initialize the database."""
    print("🚀 Flask Story Website Database Initialization")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create database
    if create_database():
        # Ask if user wants sample data
        response = input("\nDo you want to add sample stories and articles? (Y/n): ")
        if response.lower() != 'n':
            populate_sample_data()
        
        display_database_info()
        
        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("1. Make sure you have Flask installed: pip install Flask")
        print("2. Copy your HTML templates to the templates/ directory")
        print("3. Run your Flask app: python app.py")
        print("4. Visit http://localhost:5000 to see your website")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()