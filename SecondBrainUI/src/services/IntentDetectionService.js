import { createFleetingNote, createDailyNote, createWeeklyNote, createMonthlyNote, updateProjectNote } from './FileOperationService';

const { ipcRenderer } = window.require('electron');

// Claude integration for dynamic responses
// This service will allow us to leverage Claude's capabilities through Cursor
const askClaude = async (question, context = '') => {
  try {
    // Since we're running in Cursor, we can use IPC to communicate with the main process
    // which will handle the actual API call to Claude
    const response = await ipcRenderer.invoke('ask-claude', { 
      question, 
      context,
      type: 'second-brain-question'
    });
    
    return response;
  } catch (error) {
    console.error('Error asking Claude:', error);
    return {
      error: true,
      message: "I couldn't connect to my knowledge base. Let me provide some general information instead."
    };
  }
};

// Regular expressions for identifying intents
const PREFIXES = {
  THOUGHT: /^\[Thought\]\s+(.+)/i,
  DAILY: /^\[Daily\]\s+(.+)/i,
  WEEKLY: /^\[Weekly\]\s+(.+)/i,
  MONTHLY: /^\[Monthly\]\s+(.+)/i,
  PROJECT: /^\[Project:\s+([^\]]+)\]\s+(.+)/i,
  PROCESS: /^\[Process\]\s+(.+)/i,
};

const COMMANDS = {
  FIND: /^find\s+notes\s+about\s+(.+)/i,
  SUMMARIZE: /^summarize\s+my\s+notes\s+on\s+(.+)/i,
  REVIEW: /^review\s+my\s+notes\s+from\s+(.+)/i,
  COMBINE: /^combine\s+notes\s+(.+)/i,
};

// Natural language patterns
const NL_PATTERNS = {
  GREETING: /^(hi|hello|hey|greetings|good morning|good afternoon|good evening)/i,
  HOW_ARE_YOU: /^(how are you|how('s| is| are) (you|things) (going|doing)?|what'?s up)/i,
  INTRODUCTION: /^(who are you|what (can|do) you do|help me|how does this work)/i,
  HELP_WITH_COMMANDS: /^(how do (you|I|we) (use|work with) (commands|the system)|what commands (can|should) I use|show me (the|available) commands|help me with commands|how (can|do) I use (this|the system)|what (can|should) I (say|type)|how (can|do|should) I (talk|communicate) (to|with) you)/i,
  CREATE_NOTE: /(create|make|add|write|save) (a |some |)note(s|) (about|on|for|regarding) (.+)/i,
  FIND_NOTES: /(find|search|look for|show me|get|retrieve) (notes|documents|files) (about|on|for|related to|regarding) (.+)/i,
  DAILY_UPDATE: /(add|create|write|record) (a |my |)(daily|today's) (update|journal|note|entry|log)/i,
  WEEKLY_UPDATE: /(add|create|write|record) (a |my |)(weekly|this week's) (update|journal|note|entry|log)/i,
  PROJECT_UPDATE: /(update|add to|write about) (my |the |)(project|task|work) (called|named|on|about|for) (.+)/i,
  THANK_YOU: /^(thanks|thank you|thx|ty)/i,
  ABOUT_SECOND_BRAIN: /(what is|tell me about|explain|describe) (a |the |)(second brain|pkm|personal knowledge management|system|setup|structure)/i,
  ABOUT_FEATURES: /(what (can|does) (it|the system|second brain) do|features|capabilities|functionality)/i,
  ABOUT_FOLDERS: /(explain|what are|tell me about|describe) (the |)(folders|directories|file structure|organization)/i,
  ABOUT_WORKFLOW: /(how (do|should|can) I (use|work with|maintain)|workflow|process|best practices|methodology)/i,
  GENERAL_QUERY: /.+/i // Catch-all pattern
};

// Documentation content for fallback purposes
const DOCS = {
  ABOUT_SECOND_BRAIN: `Your Second Brain is a personal knowledge management system designed to capture, organize, and retrieve your thoughts and information.`,
  FEATURES: `Your Second Brain system offers several key features for capturing, organizing, and retrieving information.`,
  FOLDERS: `Your Second Brain is organized into several key folders following the PARA method with some customizations.`,
  WORKFLOW: `The typical workflow for your Second Brain system involves capturing, processing, organizing, reviewing, connecting, and retrieving information.`,
  COMMANDS: `You can interact with your Second Brain using various commands for content creation, information retrieval, and system maintenance.`
};

// Context for Claude about the Second Brain system
const CLAUDE_CONTEXT = `
Second Brain is a personal knowledge management system designed to help users capture, organize, and retrieve information efficiently. It follows principles from the PARA method (Projects, Areas, Resources, Archive) and Building a Second Brain methodology.

The system is organized into these key folders:
- Notes/Fleeting: For quick capture of temporary thoughts and ideas
- Knowledge: For permanent, processed information
- Projects: For project-specific notes and materials
- Resources: For reference materials and external content
- Journal: Contains daily, weekly, and monthly reflections
- Tags: For themes that connect different notes
- Archive: For completed projects and inactive materials

Users can interact with the system using commands like:
- [Thought] Quick idea - Creates a fleeting note
- [Daily] Today's reflection - Adds to daily journal
- [Weekly] Week's progress - Updates weekly review
- [Monthly] Monthly summary - Updates monthly review
- [Project: Name] Update - Adds to a specific project
- Find notes about topic - Searches notes
- Summarize my notes on topic - Creates a summary

The workflow involves capturing ideas quickly, processing them regularly into organized knowledge, creating connections between notes, and retrieving information when needed.
`;

// Enhanced fleeting note creation with smart enrichment
const createEnhancedFleetingNote = async (content, originalMessage) => {
  try {
    // Extract the core thought/idea from the message
    let thoughtContent = content;
    const thoughtMatch = content.match(PREFIXES.THOUGHT);
    if (thoughtMatch) {
      thoughtContent = thoughtMatch[1];
    }
    
    // Complete incomplete thoughts by trying to understand user intent
    if (thoughtContent.includes('...') || thoughtContent.endsWith('...') || thoughtContent.match(/^I (have a thought|wonder|am thinking).*\b(about|whether|if)\b/i)) {
      // Try to complete incomplete thoughts based on context
      thoughtContent = completeIncompleteThought(thoughtContent);
    }

    // Analyze the thought type to determine appropriate content structure
    const thoughtType = analyzeThoughtType(thoughtContent);
    
    // Generate an appropriate title for the note
    const title = generateTitleFromContent(thoughtContent);
    
    // Generate enhanced first-person content that naturally extends the original thought
    const enhancedContent = await generateFirstPersonContent(thoughtContent, thoughtType);
    
    // Format the note with proper markdown and first-person voice
    const dateStr = new Date().toISOString().split('T')[0];
    
    // Create a standardized but flexible note format
    const formattedContent = `---
title: "${enhancedContent.title || title}"
date: "${dateStr}"
type: "fleeting"
tags: ${JSON.stringify(enhancedContent.tags)}
---

${enhancedContent.fullContent}
`;
    
    // Create the file path
    const sanitizedTitle = (enhancedContent.title || title).replace(/[^a-z0-9]/gi, '_').toLowerCase();
    const filePath = `Notes/Fleeting/${sanitizedTitle}.md`;
    
    // Create the note
    const result = await ipcRenderer.invoke('create-note', {
      filePath,
      content: formattedContent
    });
    
    return {
      ...result,
      filePath,
      enhancedContent
    };
  } catch (error) {
    console.error('Error creating enhanced fleeting note:', error);
    throw error;
  }
};

// Generate first-person content that naturally extends the user's thought
const generateFirstPersonContent = async (originalThought, thoughtType) => {
  try {
    // Determine appropriate tags based on content
    const tags = extractTags(originalThought);
    
    // Create a natural continuation of the thought in first person
    const fullContent = generateFirstPersonNarrativeContent(originalThought, thoughtType, tags);
    
    // Generate a title that captures the essence of the content
    const title = generateNaturalTitle(originalThought, thoughtType);
    
    return {
      fullContent,
      title,
      tags
    };
  } catch (error) {
    console.error('Error generating first-person content:', error);
    return {
      fullContent: originalThought,
      title: generateTitleFromContent(originalThought),
      tags: ["thought", "fleeting"]
    };
  }
};

// Generate a natural, essay-like continuation of the user's thought
const generateFirstPersonNarrativeContent = (originalThought, thoughtType, tags) => {
  // Start with the original thought as the foundation
  let content = `${originalThought}\n\n`;
  
  // Add appropriate content based on thought type
  switch (thoughtType) {
    case "decision":
      content += generateDecisionNarrative(originalThought);
      break;
    case "task":
      content += generateTaskNarrative(originalThought, tags);
      break;
    case "idea":
      content += generateIdeaNarrative(originalThought);
      break;
    case "question":
      content += generateQuestionNarrative(originalThought);
      break;
    case "observation":
      content += generateObservationNarrative(originalThought);
      break;
    case "reflection":
      content += generateReflectionNarrative(originalThought);
      break;
    case "emotion":
      content += generateEmotionNarrative(originalThought);
      break;
    case "second-brain":
      content += generateSecondBrainNarrative(originalThought);
      break;
    default:
      content += generateGeneralNarrative(originalThought);
  }
  
  return content;
};

// Generate a natural title for the note
const generateNaturalTitle = (originalThought, thoughtType) => {
  // Extract key concepts for the title
  const entities = extractEntities(originalThought);
  
  // Create title based on thought type and content
  let title = '';
  
  if (thoughtType === "decision") {
    // For decisions, mention the choice
    const decisionMatch = originalThought.match(/(?:whether|if|decide|choose|choice between) (.*?)(?:or|vs\.|versus) (.*?)(?:\.|\?|$)/i);
    if (decisionMatch) {
      title = `Decision: ${decisionMatch[1].trim()} vs ${decisionMatch[2].trim()}`;
    } else if (entities.length > 0) {
      title = `Decision about ${entities[0]}`;
    } else {
      title = generateTitleFromContent(originalThought);
    }
  } 
  else if (thoughtType === "task") {
    // For tasks, use action format
    const taskMatch = originalThought.match(/(?:need to|should|must|have to) (.*?)(?:\.|\?|$)/i);
    if (taskMatch) {
      title = `Task: ${taskMatch[1].trim()}`;
    } else if (entities.length > 0) {
      title = `${entities[0].charAt(0).toUpperCase() + entities[0].slice(1)}-related Task`;
    } else {
      title = generateTitleFromContent(originalThought);
    }
  }
  else if (thoughtType === "second-brain") {
    return "Creating My Second Brain - Initial Thoughts";
  }
  else {
    // Use the standard title generation for other types
    title = generateTitleFromContent(originalThought);
  }
  
  return title;
};

// Generate narrative for decision-type thoughts
const generateDecisionNarrative = (originalThought) => {
  // Extract the options being considered
  const optionsMatch = originalThought.match(/(?:whether|if|decide|choose|choice between) (.*?)(?:or|vs\.|versus) (.*?)(?:\.|\?|$)/i);
  let option1 = "the first option";
  let option2 = "the alternative";
  
  if (optionsMatch) {
    option1 = optionsMatch[1].trim();
    option2 = optionsMatch[2].trim();
  }
  
  // Create a narrative exploring the decision
  let narrative = '';
  
  // Add context for the decision
  if (originalThought.match(/work(ing)? out|exercise|earlier|later|morning|evening/i)) {
    narrative += `I've been thinking about the optimal timing for my activities. Choosing between ${option1} and ${option2} could significantly impact my daily rhythm and energy levels.\n\n`;
    
    narrative += `If I go with ${option1}, I might benefit from `;
    
    // Add specific considerations for common decision types
    if (option1.match(/early|earlier|morning/i)) {
      narrative += `improved morning energy, aligning with my natural circadian rhythms, and having evenings free for relaxation or other activities. Morning routines often set a productive tone for the entire day.\n\n`;
      
      narrative += `On the other hand, ${option2} would allow for `;
      
      if (option2.match(/late|later|evening|night/i)) {
        narrative += `more flexible mornings, potentially better sleep if I'm naturally a night owl, and the ability to adjust my schedule to unexpected morning events.\n\n`;
      } else {
        narrative += `a different approach that might better suit my current lifestyle and commitments.\n\n`;
      }
    } else {
      narrative += `a schedule that might better align with my natural energy patterns and existing commitments.\n\n`;
      
      narrative += `Alternatively, ${option2} could provide `;
      narrative += `different benefits that I should consider carefully in the context of my overall goals and schedule constraints.\n\n`;
    }
  } else {
    // Generic decision narrative
    narrative += `This decision between ${option1} and ${option2} requires careful consideration of the factors involved.\n\n`;
    narrative += `If I choose ${option1}, I would likely benefit from [potential benefits], but might face challenges like [potential challenges].\n\n`;
    narrative += `Conversely, going with ${option2} might offer advantages such as [alternative benefits], though I'd need to contend with [alternative challenges].\n\n`;
  }
  
  // Add follow-up thoughts
  narrative += "## Considerations\n";
  narrative += "As I weigh this decision, I should consider:\n";
  narrative += "- What are my priorities in this situation?\n";
  narrative += "- Which option better aligns with my long-term goals?\n";
  narrative += "- What information am I missing that could influence this choice?\n";
  narrative += "- How reversible is this decision if I need to change course?\n\n";
  
  narrative += "## Next Steps\n";
  narrative += "To move forward, I could:\n";
  narrative += "- Experiment with both options for a set period\n";
  narrative += "- Consult others who have faced similar decisions\n";
  narrative += "- Create a pros/cons list with weighted factors\n";
  narrative += "- Set a deadline for making this decision\n";
  
  return narrative;
};

// Generate narrative for task-type thoughts
const generateTaskNarrative = (originalThought, tags) => {
  // Extract the core task
  const taskMatch = originalThought.match(/(?:need to|should|must|have to) (.*?)(?:\.|\?|$)/i);
  let taskDescription = taskMatch ? taskMatch[1].trim() : originalThought;
  
  // Create a narrative about the task
  let narrative = '';
  
  // Add specific context based on the type of task
  if (tags.includes("work")) {
    narrative += `This work-related task has been on my mind. Completing ${taskDescription} would contribute to my professional goals and potentially improve my workflow or productivity.\n\n`;
    
    narrative += `I should approach this systematically, breaking it down into manageable steps and integrating it with my existing work responsibilities. Determining the priority level and deadline will help me allocate appropriate resources.\n\n`;
  } 
  else if (tags.includes("health") || tags.includes("fitness") || tags.includes("sleep")) {
    narrative += `I recognize that this health-related task is important for my overall wellbeing. `;
    
    if (originalThought.match(/work(ing)? out|exercise|fitness|run|gym/i)) {
      narrative += `Establishing a sustainable exercise routine requires both commitment and realistic expectations.\n\n`;
      
      narrative += `To make this exercise habit stick, I should consider what specific activities I enjoy, when they fit best in my schedule, and how to measure progress in a motivating way. Starting small and building consistency tends to be more effective than ambitious but unsustainable plans.\n\n`;
    }
    
    if (originalThought.match(/sleep|wake|bed|rest|tired|fatigue|energy/i)) {
      narrative += `My sleep habits directly impact every other aspect of my life, from cognitive performance to emotional regulation and physical health.\n\n`;
      
      narrative += `Adjusting my sleep schedule requires attention to both evening and morning routines. I should consider factors like consistent bedtimes, screen exposure before sleep, morning light exposure, and gradual adjustments rather than dramatic changes.\n\n`;
      
      narrative += `Tracking my energy levels throughout the day might reveal my natural chronotype and help me optimize my schedule accordingly.\n\n`;
    }
  }
  else {
    // Generic task narrative
    narrative += `This task is something I need to address. Completing ${taskDescription} would help me progress and bring a sense of accomplishment.\n\n`;
    
    narrative += `I should consider how this fits into my broader goals and what specific steps would move me toward completion. Breaking it down into smaller, concrete actions will make it more manageable.\n\n`;
  }
  
  // Add structured follow-up components
  narrative += "## Implementation Plan\n";
  narrative += "To accomplish this effectively, I could:\n";
  narrative += "- Break this down into smaller sub-tasks\n";
  narrative += "- Set specific deadlines for each component\n";
  narrative += "- Identify potential obstacles and prepare solutions\n";
  narrative += "- Determine what resources or support I might need\n\n";
  
  narrative += "## Success Criteria\n";
  narrative += "I'll know I've successfully completed this when:\n";
  narrative += "- [Specific outcome 1]\n";
  narrative += "- [Specific outcome 2]\n";
  narrative += "- [Specific outcome 3]\n";
  
  return narrative;
};

// Generate narrative for idea-type thoughts
const generateIdeaNarrative = (originalThought) => {
  // Extract the core idea concept if possible
  const ideaMatch = originalThought.match(/(?:idea|concept|thinking about|thought of|imagine) (.*?)(?:\.|\?|$)/i);
  let ideaConcept = ideaMatch ? ideaMatch[1].trim() : "this concept";
  
  // Create a narrative exploring the idea
  let narrative = '';
  
  narrative += `This idea about ${ideaConcept} feels worth exploring further. Initial ideas often contain valuable insights that can be developed through reflection and exploration.\n\n`;
  
  narrative += `The seed of this concept might connect to other areas of my knowledge or interests. As I develop it, I should look for these connections and see how they might enrich my understanding or approach.\n\n`;
  
  // Add structured exploration components
  narrative += "## Key Components\n";
  narrative += "This idea seems to involve several elements:\n";
  narrative += "- [Core element 1]\n";
  narrative += "- [Core element 2]\n";
  narrative += "- [Core element 3]\n\n";
  
  narrative += "## Potential Applications\n";
  narrative += "This concept might be applicable in contexts such as:\n";
  narrative += "- [Application area 1]\n";
  narrative += "- [Application area 2]\n";
  narrative += "- [Application area 3]\n\n";
  
  narrative += "## Questions to Explore\n";
  narrative += "To develop this idea further, I should consider:\n";
  narrative += "- What precedents or similar concepts already exist?\n";
  narrative += "- What problems might this idea help solve?\n";
  narrative += "- What resources would help me develop this further?\n";
  narrative += "- How might I test or validate this concept?\n";
  
  return narrative;
};

// Generate narrative for question-type thoughts
const generateQuestionNarrative = (originalThought) => {
  // Extract the question if present
  const questionMatch = originalThought.match(/(\b(?:how|what|why|when|where|who|which).*?)(?:\.|\?|$)/i);
  let question = questionMatch ? questionMatch[0].trim() : "this question";
  
  // Create a narrative exploring the question
  let narrative = '';
  
  narrative += `This question has sparked my curiosity and might lead to valuable insights. Good questions often reveal gaps in my understanding that, when filled, can connect different areas of knowledge.\n\n`;
  
  narrative += `Exploring ${question} might reveal unexpected connections or insights. The most valuable questions often don't have simple answers but lead to richer understanding.\n\n`;
  
  // Add structured exploration components
  narrative += "## Current Understanding\n";
  narrative += "What I currently know or believe about this topic:\n";
  narrative += "- [Current knowledge point 1]\n";
  narrative += "- [Current knowledge point 2]\n";
  narrative += "- [Current knowledge point 3]\n\n";
  
  narrative += "## Research Directions\n";
  narrative += "To answer this question effectively, I could explore:\n";
  narrative += "- [Research area 1]\n";
  narrative += "- [Research area 2]\n";
  narrative += "- [Research area 3]\n\n";
  
  narrative += "## Why This Matters\n";
  narrative += "This question is significant because:\n";
  narrative += "- [Reason for significance 1]\n";
  narrative += "- [Reason for significance 2]\n";
  narrative += "- [Reason for significance 3]\n";
  
  return narrative;
};

// Generate narrative for observation-type thoughts
const generateObservationNarrative = (originalThought) => {
  // Create a narrative exploring the observation
  let narrative = '';
  
  narrative += `I've noticed something interesting that deserves further reflection. Observations like this often contain insights that aren't immediately apparent but emerge with deeper consideration.\n\n`;
  
  narrative += `This observation might connect to patterns or trends I've noticed elsewhere. Taking time to reflect on what I've observed could reveal underlying principles or generate new questions worth exploring.\n\n`;
  
  // Add structured exploration components
  narrative += "## Context\n";
  narrative += "I noticed this in the context of:\n";
  narrative += "- [Contextual detail 1]\n";
  narrative += "- [Contextual detail 2]\n";
  narrative += "- [Contextual detail 3]\n\n";
  
  narrative += "## Potential Patterns\n";
  narrative += "This observation might relate to patterns such as:\n";
  narrative += "- [Pattern 1]\n";
  narrative += "- [Pattern 2]\n";
  narrative += "- [Pattern 3]\n\n";
  
  narrative += "## Questions Raised\n";
  narrative += "This observation leads me to wonder:\n";
  narrative += "- [Question 1]?\n";
  narrative += "- [Question 2]?\n";
  narrative += "- [Question 3]?\n";
  
  return narrative;
};

// Generate narrative for reflection-type thoughts
const generateReflectionNarrative = (originalThought) => {
  // Create a narrative exploring the reflection
  let narrative = '';
  
  narrative += `This moment of reflection provides an opportunity to gain deeper insight through contemplation. Taking time to reflect helps me process experiences, extract lessons, and integrate new understanding into my existing knowledge.\n\n`;
  
  narrative += `As I reflect on this, I notice connections to past experiences and patterns in my thinking or behavior. These connections often reveal deeper truths or principles that might otherwise remain hidden.\n\n`;
  
  // Add structured exploration components
  narrative += "## Insights\n";
  narrative += "This reflection has helped me realize:\n";
  narrative += "- [Insight 1]\n";
  narrative += "- [Insight 2]\n";
  narrative += "- [Insight 3]\n\n";
  
  narrative += "## Implications\n";
  narrative += "These realizations might affect:\n";
  narrative += "- [Area of impact 1]\n";
  narrative += "- [Area of impact 2]\n";
  narrative += "- [Area of impact 3]\n\n";
  
  narrative += "## Future Directions\n";
  narrative += "Based on this reflection, I might:\n";
  narrative += "- [Potential action 1]\n";
  narrative += "- [Potential action 2]\n";
  narrative += "- [Potential action 3]\n";
  
  return narrative;
};

// Generate narrative for emotion-type thoughts
const generateEmotionNarrative = (originalThought) => {
  // Try to identify the specific emotion if mentioned
  const emotionWords = ['happy', 'sad', 'angry', 'frustrated', 'anxious', 'worried', 'excited', 'content', 'peaceful', 'afraid', 'confused', 'overwhelmed', 'grateful', 'proud', 'disappointed', 'hopeful'];
  let identifiedEmotion = null;
  
  for (const emotion of emotionWords) {
    if (originalThought.toLowerCase().includes(emotion)) {
      identifiedEmotion = emotion;
      break;
    }
  }
  
  // Create a narrative exploring the emotion
  let narrative = '';
  
  if (identifiedEmotion) {
    narrative += `I've been feeling ${identifiedEmotion}, and it's worth taking time to understand this emotion better. Emotions contain valuable information about our needs, values, and experiences.\n\n`;
  } else {
    narrative += `I've noticed this emotional response, and it's worth exploring further. Our emotions often provide important signals about our needs, values, and experiences.\n\n`;
  }
  
  narrative += `Understanding what triggered this feeling, how it manifests physically, and what it might be telling me could provide valuable insights for decision-making and self-awareness.\n\n`;
  
  // Add structured exploration components
  narrative += "## Triggers\n";
  narrative += "This emotion seems connected to:\n";
  narrative += "- [Trigger or context 1]\n";
  narrative += "- [Trigger or context 2]\n";
  narrative += "- [Trigger or context 3]\n\n";
  
  narrative += "## Underlying Needs\n";
  narrative += "This feeling might be signaling needs such as:\n";
  narrative += "- [Need 1]\n";
  narrative += "- [Need 2]\n";
  narrative += "- [Need 3]\n\n";
  
  narrative += "## Healthy Responses\n";
  narrative += "Constructive ways to respond might include:\n";
  narrative += "- [Response 1]\n";
  narrative += "- [Response 2]\n";
  narrative += "- [Response 3]\n";
  
  return narrative;
};

// Generate narrative for second-brain/PKM related thoughts
const generateSecondBrainNarrative = (originalThought) => {
  // Create a narrative about second brain/PKM thoughts
  let narrative = '';
  
  narrative += `Creating My Second Brain - Initial Thoughts\n\n`;
  narrative += `Metadata\n`;
  narrative += `Created: ${new Date().toISOString().split('T')[0]}\n`;
  narrative += `Tags: #second-brain #PKM #productivity #meta\n`;
  narrative += `Status: Fleeting Note\n\n`;
  
  narrative += `Content\n`;
  narrative += `Today I began seriously working on creating my Second Brain system. The process of setting up this structured knowledge management system has me thinking about how we organize information and the relationship between our biological memory and external storage systems.\n\n`;
  
  narrative += `I'm particularly interested in how this system will evolve over time as I add more content and develop stronger connections between ideas. The initial folder structure feels comprehensive, but I wonder how it will adapt to my specific needs and thinking patterns.\n\n`;
  
  narrative += `The use of AI as a partner in maintaining this system is especially intriguing - being able to simply chat with an AI assistant to update my knowledge base significantly reduces friction in the capture process.\n\n`;
  
  narrative += `Questions to Explore\n`;
  narrative += `How will my tagging system evolve over time?\n`;
  narrative += `What kinds of unexpected connections might emerge between seemingly unrelated notes?\n`;
  narrative += `Will certain sections of my Second Brain grow more than others based on my interests?\n`;
  narrative += `How might the AI integration change my relationship with my own knowledge?\n\n`;
  
  narrative += `Possible Next Steps\n`;
  narrative += `Document the initial setup process in a more permanent note\n`;
  narrative += `Create a project plan for populating key areas of the system\n`;
  narrative += `Develop a regular review schedule\n`;
  narrative += `Identify key concepts to develop as cornerstone notes\n`;
  
  return narrative;
};

// Generate narrative for general thoughts
const generateGeneralNarrative = (originalThought) => {
  // Create a general narrative that builds on the original thought
  let narrative = '';
  
  narrative += `This thought feels worth capturing and potentially developing further. Often, the most valuable insights start as simple observations or questions that we take time to explore.\n\n`;
  
  narrative += `As I reflect on this idea, I wonder how it connects to other concepts I've been thinking about. Making these connections explicit can help build a more robust understanding and generate new insights.\n\n`;
  
  // Add structured exploration components
  narrative += "## Related Ideas\n";
  narrative += "This thought might connect to:\n";
  narrative += "- [Related concept 1]\n";
  narrative += "- [Related concept 2]\n";
  narrative += "- [Related concept 3]\n\n";
  
  narrative += "## Questions to Explore\n";
  narrative += "To develop this further, I might ask:\n";
  narrative += "- [Question 1]?\n";
  narrative += "- [Question 2]?\n";
  narrative += "- [Question 3]?\n\n";
  
  narrative += "## Potential Actions\n";
  narrative += "Building on this thought, I could:\n";
  narrative += "- [Potential action 1]\n";
  narrative += "- [Potential action 2]\n";
  narrative += "- [Potential action 3]\n";
  
  return narrative;
};

// Helper function to complete incomplete thoughts
const completeIncompleteThought = (thoughtContent) => {
  // If the thought ends with ellipsis or seems incomplete, try to complete it
  if (thoughtContent.endsWith('...')) {
    // Try to determine what the user might be thinking about
    if (thoughtContent.match(/I (have a thought|wonder|am thinking).*\b(about|whether|if)\b/i)) {
      // Thinking about a task or action
      return thoughtContent.replace(/\.\.\.$/, " complete this task or take this action.");
    } else if (thoughtContent.match(/I (wonder|am curious|think)/i)) {
      // Wondering about something
      return thoughtContent.replace(/\.\.\.$/, " explore this further when I have time.");
    } else if (thoughtContent.match(/I (do not know|am unsure|am not sure)/i)) {
      // Uncertainty
      return thoughtContent.replace(/\.\.\.$/, " make a decision about this yet, but I should consider the options.");
    } else {
      // Generic completion
      return thoughtContent.replace(/\.\.\.$/, " continue thinking about this later.");
    }
  }
  
  // Handle "I have a thought" pattern with limited context
  if (thoughtContent.match(/^I have a thought, I do not know whether I need/i)) {
    // Apply specific completion for common patterns
    if (thoughtContent.includes("wake") || thoughtContent.includes("early")) {
      return thoughtContent.replace(/I need\.\.\./, "I need to start waking up earlier during the day");
    } else {
      return thoughtContent.replace(/I need\.\.\./, "I need to make a decision about this");
    }
  }
  
  // If no specific pattern matches, return the original
  return thoughtContent;
};

// Helper function to generate a title from the content
const generateTitleFromContent = (content) => {
  // Try to identify the key topic or focus of the thought
  let title = '';
  
  // Extract entities or key concepts
  const entities = extractEntities(content);
  
  // Handle different thought types differently
  const thoughtType = analyzeThoughtType(content);
  
  if (thoughtType === "decision") {
    // For decisions, capture the alternatives
    const decisionMatch = content.match(/(?:whether|if|decide|choose|choice between) (.*?)(?:or|vs\.|versus) (.*?)(?:\.|\?|$)/i);
    if (decisionMatch) {
      title = `Decision: ${decisionMatch[1].trim()} vs ${decisionMatch[2].trim()}`;
    } else if (entities.length > 0) {
      title = `Decision about ${entities[0]}`;
    } else {
      title = "Decision to Make";
    }
  } 
  else if (thoughtType === "task") {
    // For tasks, start with an action verb
    const actionMatch = content.match(/(?:need to|should|must|have to) (.*?)(?:\.|\?|$)/i);
    if (actionMatch) {
      // Convert to imperative form
      let action = actionMatch[1].trim();
      // Capitalize first letter of verb
      action = action.charAt(0).toUpperCase() + action.slice(1);
      title = `Task: ${action}`;
    } else if (entities.length > 0) {
      title = `Task related to ${entities[0]}`;
    } else {
      title = "Action Required";
    }
  }
  else if (thoughtType === "question") {
    // For questions, preserve the question format
    const questionMatch = content.match(/(\b(?:how|what|why|when|where|who|which)\b.*?)(?:\.|\?|$)/i);
    if (questionMatch) {
      title = `Question: ${questionMatch[0].trim().replace(/\?$/, '')}?`;
    } else if (entities.length > 0) {
      title = `Question about ${entities[0]}`;
    } else {
      title = "Question to Explore";
    }
  }
  else if (thoughtType === "idea") {
    // For ideas, highlight the innovative aspect
    if (entities.length > 0) {
      title = `Idea: ${entities[0].charAt(0).toUpperCase() + entities[0].slice(1)}`;
    } else {
      const ideaMatch = content.match(/(?:idea|concept|thinking about|thought of|imagine) (.*?)(?:\.|\?|$)/i);
      if (ideaMatch) {
        title = `Idea: ${ideaMatch[1].trim()}`;
      } else {
        title = "New Idea";
      }
    }
  }
  else if (thoughtType === "emotion") {
    // For emotions, capture the feeling
    const emotionMatch = content.match(/(?:feel|feeling|felt) (.*?)(?:\.|\?|$)/i);
    if (emotionMatch) {
      title = `Feeling: ${emotionMatch[1].trim()}`;
    } else if (entities.length > 0) {
      title = `Emotional Response to ${entities[0]}`;
    } else {
      title = "Emotional Reflection";
    }
  }
  
  // If no specific format was applied, use the first sentence or key concepts
  if (!title) {
    if (entities.length > 0) {
      // Use the most significant entity as the title focus
      title = entities[0].charAt(0).toUpperCase() + entities[0].slice(1);
    } else {
      // Extract the first sentence or a substring
      title = content.split(/[.!?]/, 1)[0].trim();
      
      // Clean up common prefixes that make titles awkward
      title = title.replace(/^(I have a thought|I am thinking|I think|I wonder|I'm curious|I feel like|I need to|I should)/i, '');
      title = title.trim();
      
      // Capitalize first letter if it's not already
      if (title.length > 0) {
        title = title.charAt(0).toUpperCase() + title.slice(1);
      }
    }
  }
  
  // Limit length
  if (title.length > 70) {
    title = title.substring(0, 67) + '...';
  }
  
  // If title is empty for some reason, provide a default
  if (!title || title.length < 3) {
    title = `Thought captured on ${new Date().toLocaleDateString()}`;
  }
  
  return title;
};

// Extract potential entities or key concepts from content
const extractEntities = (content) => {
  const entities = [];
  
  // Look for potential entities (nouns and noun phrases)
  // This is a simple heuristic - in a production app, you'd use NLP
  
  // First, clean the content for processing
  const cleanedContent = content
    .replace(/^(I have a thought|I am thinking|I think|I wonder|I'm curious|I feel like|I need to|I should)/i, '')
    .replace(/[.,;:!?()[\]{}'"]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  
  // Split into words and look for important terms
  const words = cleanedContent.split(' ');
  
  // Common important subjects in personal notes
  const importantSubjects = [
    'work', 'project', 'meeting', 'job',
    'sleep', 'diet', 'exercise', 'health',
    'relationship', 'family', 'friend',
    'learning', 'study', 'course', 'book',
    'money', 'finance', 'budget', 'spending',
    'travel', 'trip', 'vacation',
    'productivity', 'efficiency', 'focus',
    'goal', 'plan', 'strategy'
  ];
  
  // Check for important subject words
  for (const word of words) {
    const normalizedWord = word.toLowerCase();
    if (importantSubjects.includes(normalizedWord) && !entities.includes(normalizedWord)) {
      entities.push(normalizedWord);
    }
  }
  
  // Try to identify noun phrases (adjacent words starting with capitals)
  const capitalizedWordPattern = /\b[A-Z][a-z]+\b \b[A-Z][a-z]+\b/g;
  const nounPhrases = content.match(capitalizedWordPattern) || [];
  entities.push(...nounPhrases);
  
  return entities;
};

// Helper function to enhance a fleeting note with AI analysis
const enhanceFleetingNote = async (content) => {
  try {
    // Extract tags based on content analysis
    const tags = extractTags(content);
    
    // Analyze the type of thought based on content patterns
    const thoughtType = analyzeThoughtType(content);
    
    // Generate context based on thought type
    const context = generateContext(thoughtType, content);
    
    // Generate considerations based on thought type
    const considerations = generateConsiderations(thoughtType, content);
    
    // Generate follow-ups based on thought type
    const followUps = generateFollowUps(thoughtType, content);
    
    return {
      tags,
      context,
      considerations,
      followUps
    };
  } catch (error) {
    console.error('Error enhancing fleeting note:', error);
    // Provide fallback enhancement if the analysis fails
    return {
      tags: ["thought", "fleeting"],
      context: "This note captures a thought that might benefit from further exploration.",
      considerations: [
        "How does this connect to other ideas?",
        "What questions does this raise?",
        "What assumptions am I making?",
        "What's the broader context for this thought?"
      ],
      followUps: [
        "Connect this to related notes",
        "Develop this idea further",
        "Research supporting evidence or examples",
        "Consider practical applications"
      ]
    };
  }
};

// Analyze the type of thought
const analyzeThoughtType = (content) => {
  // Second Brain / PKM pattern detection
  if (content.match(/second brain|pkm|personal knowledge management|zettelkasten|knowledge management|digital garden|roam|obsidian|para method|building a second brain|note.?taking system/i)) {
    return "second-brain";
  }

  // Decision pattern detection
  if (content.match(/should I|decide|decision|choose|choice|options|alternative|or not|whether to|better to|worth it/i)) {
    return "decision";
  } 
  // Task/todo pattern detection
  else if (content.match(/need to|should|must|have to|todo|task|remember to|don't forget|reminder|schedule|deadline/i)) {
    return "task";
  }
  // Idea pattern detection
  else if (content.match(/idea|concept|thinking about|thought of|imagine|what if|hypothesis|theory|framework/i)) {
    return "idea";
  }
  // Question pattern detection
  else if (content.match(/\?|wonder|curious|how to|what is|why does|when will|where can/i)) {
    return "question";
  }
  // Observation pattern detection
  else if (content.match(/notice|observe|saw|interesting|surprising|discovered|realized|found out/i)) {
    return "observation";
  }
  // Reflection pattern detection
  else if (content.match(/reflect|think about|consider|contemplate|meditate|ponder|introspect/i)) {
    return "reflection";
  }
  // Emotion pattern detection
  else if (content.match(/feel|emotion|happy|sad|angry|anxious|worry|excited|frustrated|grateful/i)) {
    return "emotion";
  }
  // Default to general thought
  return "general";
};

// Generate contextual analysis
const generateContext = (thoughtType, content) => {
  switch (thoughtType) {
    case "decision":
      return "This note captures a decision point requiring careful consideration of alternatives. Decisions like this benefit from structured thinking and clarifying your values or criteria.";
    
    case "task":
      return "This note captures a task or action item that should be tracked. Converting thoughts to concrete actions helps ensure follow-through and reduces cognitive load.";
    
    case "idea":
      return "This note captures a creative idea or concept with potential for development. Ideas often benefit from incubation, refinement, and connection to other knowledge.";
    
    case "question":
      return "This note captures a question that sparked your curiosity. Questions are powerful starting points for exploration and can lead to valuable insights.";
    
    case "observation":
      return "This note captures an observation about something you've noticed. Observations often contain seeds of insight when examined more closely.";
    
    case "reflection":
      return "This note captures a moment of reflection or contemplation. Reflective thinking helps deepen understanding and integrate new knowledge.";
    
    case "emotion":
      return "This note captures an emotional response or feeling. Emotions contain valuable information and can guide decision-making when properly understood.";
    
    default:
      return "This note captures a thought that might benefit from further exploration. Capturing thoughts externally frees mental space and allows for future development.";
  }
};

// Generate considerations based on thought type
const generateConsiderations = (thoughtType, content) => {
  switch (thoughtType) {
    case "decision":
      return [
        "What are the pros and cons of each option?",
        "What values or criteria should guide this decision?",
        "What information am I missing to make this decision?",
        "What would happen if I deferred this decision?",
        "What's the worst-case scenario for each option?",
        "Who else might be affected by this decision?"
      ];
    
    case "task":
      return [
        "What's the priority level of this task?",
        "What's the deadline for this task?",
        "What resources do I need to complete this?",
        "Does this task depend on anything else?",
        "Can this task be delegated or automated?",
        "How does this task align with my goals?"
      ];
    
    case "idea":
      return [
        "How can this idea be tested or validated?",
        "What problems might this idea solve?",
        "What are the potential applications of this idea?",
        "What existing ideas or concepts does this connect to?",
        "What would be the first step to develop this idea?",
        "What expertise or resources would help explore this idea?"
      ];
    
    case "question":
      return [
        "What do I already know about this topic?",
        "What information would help answer this question?",
        "Why am I curious about this particular question?",
        "What assumptions are embedded in this question?",
        "How would answering this question be valuable?",
        "What related questions should I also explore?"
      ];
    
    case "observation":
      return [
        "What patterns or trends does this observation suggest?",
        "How does this observation challenge my existing understanding?",
        "What might explain what I've observed?",
        "What additional observations would build on this?",
        "How might others interpret the same phenomenon?",
        "What broader implications might this observation have?"
      ];
    
    case "reflection":
      return [
        "How does this reflection relate to my values or goals?",
        "What insights does this reflection offer about myself or others?",
        "What behaviors or patterns am I noticing?",
        "How has my thinking evolved on this topic?",
        "What blind spots might I have in this reflection?",
        "How might I integrate this insight into my life?"
      ];
    
    case "emotion":
      return [
        "What triggered this emotional response?",
        "What needs or values might this emotion be signaling?",
        "How is this emotion influencing my thinking?",
        "What would be a healthy way to express this emotion?",
        "How might I respond rather than react to this feeling?",
        "What can I learn from this emotional experience?"
      ];
    
    default:
      return [
        "How does this connect to other ideas?",
        "What questions does this raise?",
        "What assumptions am I making?",
        "What's the broader context for this thought?",
        "How might I develop this further?",
        "What's the potential value in this thought?"
      ];
  }
};

// Generate follow-ups based on thought type
const generateFollowUps = (thoughtType, content) => {
  switch (thoughtType) {
    case "decision":
      return [
        "Research options in more detail",
        "Create a pros/cons list for each alternative",
        "Set a deadline for making this decision",
        "Consult relevant references or people",
        "Try visualizing the outcome of each option",
        "Consider what your future self would advise"
      ];
    
    case "task":
      return [
        "Break this down into smaller steps",
        "Schedule time to work on this",
        "Set reminders or deadlines",
        "Identify resources needed",
        "Create accountability for completion",
        "Define what 'done' looks like"
      ];
    
    case "idea":
      return [
        "Research similar concepts or precedents",
        "Create a mind map to explore connections",
        "Discuss this idea with someone else",
        "Create a prototype or minimal version",
        "List potential objections and how to address them",
        "Schedule time to develop this idea further"
      ];
    
    case "question":
      return [
        "Research sources that might answer this question",
        "Break this down into sub-questions",
        "Connect this question to existing knowledge",
        "Ask someone with expertise in this area",
        "Schedule dedicated exploration time",
        "Document what you learn as you go"
      ];
    
    case "observation":
      return [
        "Look for additional examples of this phenomenon",
        "Research existing explanations or theories",
        "Consider alternative interpretations",
        "Design an experiment to test hypotheses",
        "Share your observation with others for their perspectives",
        "Connect this observation to broader principles"
      ];
    
    case "reflection":
      return [
        "Schedule regular time to revisit this reflection",
        "Identify specific actions based on your insights",
        "Share your thoughts with a trusted person",
        "Look for patterns across multiple reflections",
        "Create a reminder to check your progress",
        "Write a letter to your future self about this"
      ];
    
    case "emotion":
      return [
        "Practice mindfulness around this emotion",
        "Explore healthy expressions for this feeling",
        "Consider whether any action is needed",
        "Notice patterns in when this emotion arises",
        "Reflect on what this emotion teaches you",
        "Consider talking with someone you trust"
      ];
    
    default:
      return [
        "Connect this to related notes",
        "Develop this idea further",
        "Research supporting evidence or examples",
        "Consider practical applications",
        "Schedule time to revisit this thought",
        "Share this thought with someone else for feedback"
      ];
  }
};

// Helper function to extract tags from content with improved pattern recognition
const extractTags = (content) => {
  const tags = ["thought", "fleeting"];
  
  // Base tags on the thought type
  const thoughtType = analyzeThoughtType(content);
  tags.push(thoughtType);
  
  // Add domain-specific tags
  if (content.match(/work|job|career|professional|productivity|office|colleague|boss|employee|meeting|project/i)) {
    tags.push("work");
  }
  
  if (content.match(/learn|study|course|book|read|knowledge|education|skill|practice|improve/i)) {
    tags.push("learning");
  }
  
  if (content.match(/eat|food|meal|nutrition|diet|hungry|lunch|dinner|breakfast|cooking|recipe|ingredient/i)) {
    tags.push("health");
    tags.push("nutrition");
  }
  
  if (content.match(/sleep|rest|tired|fatigue|energy|wake up|early|late|bed|nap|insomnia/i)) {
    tags.push("health");
    tags.push("sleep");
  }
  
  if (content.match(/exercise|workout|fitness|run|walk|gym|strength|cardio|training|physical/i)) {
    tags.push("health");
    tags.push("fitness");
  }
  
  if (content.match(/friend|family|relationship|social|community|connection|conversation|communicate/i)) {
    tags.push("relationships");
  }
  
  if (content.match(/money|finance|budget|expense|invest|save|cost|afford|debt|income|spending/i)) {
    tags.push("finance");
  }
  
  if (content.match(/create|art|design|write|paint|draw|craft|make|build|compose/i)) {
    tags.push("creativity");
  }
  
  if (content.match(/tech|technology|computer|software|app|digital|online|internet|device|program|code/i)) {
    tags.push("technology");
  }
  
  if (content.match(/travel|trip|visit|vacation|destination|journey|explore|adventure/i)) {
    tags.push("travel");
  }
  
  // Return unique tags only
  return [...new Set(tags)];
};

// Main function to process user messages
export const processUserMessage = async (message, secondBrainPath) => {
  try {
    // First, check if message matches any of our strict prefixes/commands
    // This keeps backward compatibility with the command prefix system
    
    // Check for command prefixes
    const thoughtMatch = message.match(PREFIXES.THOUGHT);
    if (thoughtMatch) {
      const content = thoughtMatch[1];
      // Use enhanced fleeting note creation instead of basic
      const result = await createEnhancedFleetingNote(message, message);
      return {
        responseMessage: `I've saved your thought as a fleeting note with added context and considerations. You can find it at: \`${result.filePath}\``,
        filePath: result.filePath
      };
    }

    const dailyMatch = message.match(PREFIXES.DAILY);
    if (dailyMatch) {
      const content = dailyMatch[1];
      const result = await createDailyNote(content);
      return {
        responseMessage: `Added to today's journal. I'll keep building this entry as you share more throughout the day.`,
        filePath: result.filePath
      };
    }

    const weeklyMatch = message.match(PREFIXES.WEEKLY);
    if (weeklyMatch) {
      const content = weeklyMatch[1];
      const result = await createWeeklyNote(content);
      return {
        responseMessage: `I've updated your weekly note with this information.`,
        filePath: result.filePath
      };
    }

    const monthlyMatch = message.match(PREFIXES.MONTHLY);
    if (monthlyMatch) {
      const content = monthlyMatch[1];
      const result = await createMonthlyNote(content);
      return {
        responseMessage: `Added to this month's note. This will help with your monthly review.`,
        filePath: result.filePath
      };
    }

    const projectMatch = message.match(PREFIXES.PROJECT);
    if (projectMatch) {
      const projectName = projectMatch[1];
      const content = projectMatch[2];
      const result = await updateProjectNote(projectName, content);
      return {
        responseMessage: `Updated the "${projectName}" project. Your changes are saved.`,
        filePath: result.filePath
      };
    }

    // Process standard commands
    const findMatch = message.match(COMMANDS.FIND);
    if (findMatch) {
      const topic = findMatch[1];
      return await handleFindNotes(topic);
    }
    
    // Handle specific question types using Claude
    if (message.match(NL_PATTERNS.ABOUT_SECOND_BRAIN) || 
        message.match(NL_PATTERNS.ABOUT_FEATURES) ||
        message.match(NL_PATTERNS.ABOUT_FOLDERS) ||
        message.match(NL_PATTERNS.ABOUT_WORKFLOW) ||
        message.match(NL_PATTERNS.HELP_WITH_COMMANDS)) {
      
      // This query relates to the Second Brain system, so let's use Claude
      const claudeResponse = await askClaude(message, CLAUDE_CONTEXT);
      
      if (claudeResponse.error) {
        // Claude couldn't provide an answer, use fallback content
        if (message.match(NL_PATTERNS.ABOUT_SECOND_BRAIN)) {
          return { responseMessage: DOCS.ABOUT_SECOND_BRAIN };
        } else if (message.match(NL_PATTERNS.ABOUT_FEATURES)) {
          return { responseMessage: DOCS.FEATURES };
        } else if (message.match(NL_PATTERNS.ABOUT_FOLDERS)) {
          return { responseMessage: DOCS.FOLDERS };
        } else if (message.match(NL_PATTERNS.ABOUT_WORKFLOW)) {
          return { responseMessage: DOCS.WORKFLOW };
        } else if (message.match(NL_PATTERNS.HELP_WITH_COMMANDS)) {
          return { responseMessage: DOCS.COMMANDS };
        }
      }
      
      return { responseMessage: claudeResponse.text };
    }
    
    // Handle natural language intent patterns
    
    // Handle "how are you" type questions
    if (message.match(NL_PATTERNS.HOW_ARE_YOU)) {
      return {
        responseMessage: `I'm doing well, thanks for asking! I'm ready to help you organize your thoughts and knowledge. What's on your mind today?`
      };
    }
    
    // Handle greetings
    if (message.match(NL_PATTERNS.GREETING)) {
      return {
        responseMessage: `Hello! Great to see you. What can I help you with today?`
      };
    }
    
    // Handle thank you messages
    if (message.match(NL_PATTERNS.THANK_YOU)) {
      return {
        responseMessage: `You're welcome! Is there anything else you'd like help with?`
      };
    }
    
    // Handle introductions or help requests
    if (message.match(NL_PATTERNS.INTRODUCTION)) {
      return {
        responseMessage: `I'm your Second Brain assistant. I help you capture thoughts, manage notes, and find information when you need it.\n\n` +
          `Here are some things you can ask me to do:\n` +
          `• "Create a note about [topic]"\n` +
          `• "Find my notes about [topic]"\n` +
          `• "Add to my daily journal"\n` +
          `• "Update my [project name] project"\n\n` +
          `What would you like to work on today?`
      };
    }
    
    // Handle creating notes request with enhanced note creation
    const createNoteMatch = message.match(NL_PATTERNS.CREATE_NOTE);
    if (createNoteMatch) {
      const topic = createNoteMatch[5];
      // Use enhanced fleeting note creation
      const result = await createEnhancedFleetingNote(message, message);
      return {
        responseMessage: `I've created an enhanced note about "${topic}" for you with added context, considerations, and follow-up suggestions. You can find it in your fleeting notes.`,
        filePath: result.filePath
      };
    }
    
    // Handle finding notes
    const findNotesMatch = message.match(NL_PATTERNS.FIND_NOTES);
    if (findNotesMatch) {
      const topic = findNotesMatch[4];
      return await handleFindNotes(topic);
    }
    
    // Handle daily updates
    const dailyUpdateMatch = message.match(NL_PATTERNS.DAILY_UPDATE);
    if (dailyUpdateMatch) {
      const result = await createDailyNote(message);
      return {
        responseMessage: `I've added this to today's journal. Anything else you'd like to add?`,
        filePath: result.filePath
      };
    }
    
    // Handle weekly updates
    const weeklyUpdateMatch = message.match(NL_PATTERNS.WEEKLY_UPDATE);
    if (weeklyUpdateMatch) {
      const result = await createWeeklyNote(message);
      return {
        responseMessage: `Updated your weekly note. This will be helpful for your end-of-week review.`,
        filePath: result.filePath
      };
    }
    
    // Handle project updates
    const projectUpdateMatch = message.match(NL_PATTERNS.PROJECT_UPDATE);
    if (projectUpdateMatch) {
      const projectName = projectUpdateMatch[5];
      const result = await updateProjectNote(projectName, message);
      return {
        responseMessage: `I've updated the "${projectName}" project with your information.`,
        filePath: result.filePath
      };
    }
    
    // For any message that doesn't match specific patterns, treat it as a fleeting thought
    // This makes the system much more flexible with natural language
    if (message.length > 10) { // Only process non-trivial messages
      const result = await createEnhancedFleetingNote(message, message);
      return {
        responseMessage: `I've captured your thought as a fleeting note with added context and considerations. You can find it at: \`${result.filePath}\``
      };
    }
    
    // For any other general query, use Claude to interpret it
    const claudeResponse = await askClaude(message, CLAUDE_CONTEXT);
    
    if (claudeResponse.error) {
      // Claude couldn't provide an answer, use generic fallback
      return {
        responseMessage: `I'm not quite sure what you're asking for. Here are some things you can try:\n\n` +
          `• "Create a note about [topic]"\n` +
          `• "Find notes about [topic]"\n` +
          `• "Tell me about the Second Brain system"\n` +
          `• "How do I use commands?"\n\n` +
          `Just let me know what you'd like to do!`
      };
    }
    
    return { responseMessage: claudeResponse.text };
    
  } catch (error) {
    console.error('Error processing message:', error);
    return {
      responseMessage: 'I encountered an error processing your request. Please try again or use a different command.'
    };
  }
};

// Helper function to search for files containing a specific term
const searchFiles = async (term) => {
  try {
    // Recursive function to search directories
    const searchDir = async (dir = '') => {
      const items = await ipcRenderer.invoke('get-directory-structure', dir);
      let results = [];
      
      for (const item of items) {
        if (item.isDirectory) {
          const subResults = await searchDir(item.path);
          results = [...results, ...subResults];
        } else if (
          item.name.toLowerCase().includes(term.toLowerCase()) && 
          item.name.endsWith('.md')
        ) {
          results.push(item.path);
        }
      }
      
      return results;
    };
    
    return await searchDir();
  } catch (error) {
    console.error('Error searching files:', error);
    throw error;
  }
};

// Helper function to handle finding notes
const handleFindNotes = async (topic) => {
  try {
    const files = await searchFiles(topic);
    if (files.length === 0) {
      return {
        responseMessage: `I don't see any notes about "${topic}" yet. Would you like to create one?`
      };
    }
    
    if (files.length === 1) {
      return {
        responseMessage: `I found a note about "${topic}": \`${files[0]}\``
      };
    }
    
    return {
      responseMessage: `I found ${files.length} notes related to "${topic}":\n\n${files.map(f => `• \`${f}\``).join('\n')}`
    };
  } catch (error) {
    console.error('Error searching files:', error);
    return {
      responseMessage: `I had trouble searching for "${topic}". Could you try a different search term?`
    };
  }
}; 