#!/usr/bin/env node
/**
 * Perplexity MCP Server
 * Provides real-time web search capabilities to Claude Desktop via MCP
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// Configuration
const PERPLEXITY_API_KEY = process.env.PERPLEXITY_API_KEY;
const PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions';

class PerplexityMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'perplexity-search',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'web_search',
            description: 'Search the web for real-time information using Perplexity AI',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'The search query',
                },
                model: {
                  type: 'string',
                  description: 'The model to use (sonar-pro or sonar-small)',
                  default: 'sonar-pro',
                },
                max_tokens: {
                  type: 'number',
                  description: 'Maximum tokens for response',
                  default: 1000,
                },
              },
              required: ['query'],
            },
          },
          {
            name: 'research_topic',
            description: 'Conduct comprehensive research on a specific topic',
            inputSchema: {
              type: 'object',
              properties: {
                topic: {
                  type: 'string',
                  description: 'The research topic',
                },
                focus_areas: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Specific areas to focus on (optional)',
                },
              },
              required: ['topic'],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'web_search':
          return this.handleWebSearch(args);
        case 'research_topic':
          return this.handleResearchTopic(args);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async handleWebSearch(args) {
    const { query, model = 'sonar-pro', max_tokens = 1000 } = args;

    try {
      const response = await this.callPerplexityAPI(query, model, max_tokens);
      
      return {
        content: [
          {
            type: 'text',
            text: `**Web Search Results for: "${query}"**\n\n${response.content}\n\n*Source: Perplexity AI (${model})*`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error performing web search: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async handleResearchTopic(args) {
    const { topic, focus_areas = [] } = args;

    try {
      // Create comprehensive research query
      let researchQuery = `Provide comprehensive research on: ${topic}`;
      if (focus_areas.length > 0) {
        researchQuery += `. Focus specifically on: ${focus_areas.join(', ')}`;
      }
      researchQuery += '. Include latest developments, key insights, and relevant statistics.';

      const response = await this.callPerplexityAPI(researchQuery, 'sonar-pro', 2000);
      
      return {
        content: [
          {
            type: 'text',
            text: `**Comprehensive Research: "${topic}"**\n\n${response.content}\n\n*Source: Perplexity AI Research*`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error conducting research: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async callPerplexityAPI(query, model, max_tokens) {
    const response = await fetch(PERPLEXITY_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: model,
        messages: [
          {
            role: 'user',
            content: query,
          },
        ],
        max_tokens: max_tokens,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Perplexity API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      content: data.choices[0].message.content,
      usage: data.usage,
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Perplexity MCP server running on stdio');
  }
}

// Start the server
const server = new PerplexityMCPServer();
server.run().catch(console.error);