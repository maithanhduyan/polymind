import { Service } from './base-service.js';
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Schema definitions for embedding operations
const generateEmbeddingSchema = z.object({
    text: z.string().describe('Text to generate embeddings for'),
    model: z.string().optional().describe('Embedding model to use (default: nomic-embed-text)'),
    normalize: z.boolean().optional().describe('Whether to normalize embeddings (default: true)')
});

const batchEmbeddingSchema = z.object({
    texts: z.array(z.string()).describe('Array of texts to generate embeddings for'),
    model: z.string().optional().describe('Embedding model to use (default: nomic-embed-text)'),
    normalize: z.boolean().optional().describe('Whether to normalize embeddings (default: true)')
});

const preprocessTextSchema = z.object({
    text: z.string().describe('Vietnamese text to preprocess'),
    removeAccents: z.boolean().optional().describe('Remove Vietnamese accents (default: false)'),
    lowercase: z.boolean().optional().describe('Convert to lowercase (default: true)')
});

interface EmbeddingResponse {
    embedding: number[];
    model: string;
    normalized: boolean;
}

interface BatchEmbeddingResponse {
    embeddings: number[][];
    model: string;
    normalized: boolean;
    count: number;
}

export class EmbeddingService implements Service {
    private ollamaBaseUrl = 'http://localhost:11434';

    readonly namespace = 'embedding';
    readonly name = 'embedding-service';
    readonly description = 'Multi-provider embedding service with Vietnamese language optimization';
    readonly version = '1.0.0';
    constructor() {
        // Constructor logic if needed
    }
    async listTools(): Promise<{ tools: Tool[] }> {
        return {
            tools: [
                {
                    name: 'embedding_generate',
                    description: 'Generate embeddings for a single text using specified model',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            text: {
                                type: 'string',
                                description: 'Text to generate embeddings for'
                            },
                            model: {
                                type: 'string',
                                description: 'Embedding model to use (default: nomic-embed-text)',
                                default: 'nomic-embed-text'
                            },
                            normalize: {
                                type: 'boolean',
                                description: 'Whether to normalize embeddings (default: true)',
                                default: true
                            }
                        },
                        required: ['text']
                    }
                },
                {
                    name: 'embedding_batch',
                    description: 'Generate embeddings for multiple texts in batch',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            texts: {
                                type: 'array',
                                items: { type: 'string' },
                                description: 'Array of texts to generate embeddings for'
                            },
                            model: {
                                type: 'string',
                                description: 'Embedding model to use (default: nomic-embed-text)',
                                default: 'nomic-embed-text'
                            },
                            normalize: {
                                type: 'boolean',
                                description: 'Whether to normalize embeddings (default: true)',
                                default: true
                            }
                        },
                        required: ['texts']
                    }
                },
                {
                    name: 'embedding_preprocess_vietnamese',
                    description: 'Preprocess Vietnamese text for better embedding quality',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            text: {
                                type: 'string',
                                description: 'Vietnamese text to preprocess'
                            },
                            removeAccents: {
                                type: 'boolean',
                                description: 'Remove Vietnamese accents (default: false)',
                                default: false
                            },
                            lowercase: {
                                type: 'boolean',
                                description: 'Convert to lowercase (default: true)',
                                default: true
                            }
                        },
                        required: ['text']
                    }
                },
                {
                    name: 'embedding_list_models',
                    description: 'List all available embedding models',
                    inputSchema: {
                        type: 'object',
                        properties: {}
                    }
                },
                {
                    name: 'embedding_test_similarity',
                    description: 'Test similarity between two texts using embeddings',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            text1: {
                                type: 'string',
                                description: 'First text'
                            },
                            text2: {
                                type: 'string',
                                description: 'Second text'
                            },
                            model: {
                                type: 'string',
                                description: 'Model to use (default: nomic-embed-text)',
                                default: 'nomic-embed-text'
                            }
                        },
                        required: ['text1', 'text2']
                    }
                }
            ]
        };
    }

    async callTool(name: string, args: any): Promise<any> {
        switch (name) {
            case 'embedding_generate': {
                const parsedArgs = generateEmbeddingSchema.parse(args);
                const result = await this.generateEmbedding(
                    parsedArgs.text,
                    parsedArgs.model || 'nomic-embed-text',
                    parsedArgs.normalize !== false
                );
                return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
            }

            case 'embedding_batch': {
                const parsedArgs = batchEmbeddingSchema.parse(args);
                const result = await this.generateBatchEmbeddings(
                    parsedArgs.texts,
                    parsedArgs.model || 'nomic-embed-text',
                    parsedArgs.normalize !== false
                );
                return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
            }

            case 'embedding_preprocess_vietnamese': {
                const parsedArgs = preprocessTextSchema.parse(args);
                const result = this.preprocessVietnameseText(
                    parsedArgs.text,
                    parsedArgs.removeAccents || false,
                    parsedArgs.lowercase !== false
                );
                return { content: [{ type: 'text', text: result }] };
            }

            case 'embedding_list_models': {
                const result = await this.listAvailableModels();
                return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
            }

            case 'embedding_test_similarity': {
                const parsedArgs = z.object({
                    text1: z.string(),
                    text2: z.string(),
                    model: z.string().optional()
                }).parse(args);

                const result = await this.testSimilarity(
                    parsedArgs.text1,
                    parsedArgs.text2,
                    parsedArgs.model || 'nomic-embed-text'
                );
                return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
            }

            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    }

    // Public method to generate embeddings (for use by other services)
    async generateEmbeddingForText(
        text: string,
        model: string = 'nomic-embed-text',
        normalize: boolean = true
    ): Promise<EmbeddingResponse> {
        return this.generateEmbedding(text, model, normalize);
    }

    // Public method to generate batch embeddings (for use by other services)
    async generateBatchEmbeddingsForTexts(
        texts: string[],
        model: string = 'nomic-embed-text',
        normalize: boolean = true
    ): Promise<BatchEmbeddingResponse> {
        return this.generateBatchEmbeddings(texts, model, normalize);
    }

    private async generateEmbedding(
        text: string,
        model: string = 'nomic-embed-text',
        normalize: boolean = true
    ): Promise<EmbeddingResponse> {
        try {
            // Preprocess Vietnamese text
            const processedText = this.preprocessVietnameseText(text, false, true);

            const response = await fetch(`${this.ollamaBaseUrl}/api/embeddings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model,
                    prompt: processedText
                })
            });

            if (!response.ok) {
                throw new Error(`Ollama API error: ${response.statusText}`);
            }

            const data = await response.json();
            let embedding = data.embedding;

            if (normalize && embedding) {
                embedding = this.normalizeVector(embedding);
            }

            return {
                embedding,
                model,
                normalized: normalize
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            throw new Error(`Failed to generate embedding: ${errorMessage}`);
        }
    }

    private async generateBatchEmbeddings(
        texts: string[],
        model: string = 'nomic-embed-text',
        normalize: boolean = true
    ): Promise<BatchEmbeddingResponse> {
        try {
            const embeddings: number[][] = [];

            // Process texts in batches to avoid overwhelming the API
            const batchSize = 10;
            for (let i = 0; i < texts.length; i += batchSize) {
                const batch = texts.slice(i, i + batchSize);
                const batchPromises = batch.map(text =>
                    this.generateEmbedding(text, model, normalize)
                );

                const batchResults = await Promise.all(batchPromises);
                embeddings.push(...batchResults.map(r => r.embedding));
            }

            return {
                embeddings,
                model,
                normalized: normalize,
                count: embeddings.length
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            throw new Error(`Failed to generate batch embeddings: ${errorMessage}`);
        }
    }

    private preprocessVietnameseText(
        text: string,
        removeAccents: boolean = false,
        lowercase: boolean = true
    ): string {
        let processed = text;

        // Normalize whitespace
        processed = processed.replace(/\s+/g, ' ').trim();

        // Convert to lowercase if requested
        if (lowercase) {
            processed = processed.toLowerCase();
        }

        // Remove Vietnamese accents if requested
        if (removeAccents) {
            processed = this.removeVietnameseAccents(processed);
        }

        return processed;
    }

    private removeVietnameseAccents(text: string): string {
        const accentsMap: { [key: string]: string } = {
            'à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ': 'a',
            'è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ': 'e',
            'ì|í|ị|ỉ|ĩ': 'i',
            'ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ': 'o',
            'ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ': 'u',
            'ỳ|ý|ỵ|ỷ|ỹ': 'y',
            'đ': 'd'
        };

        for (const [accented, plain] of Object.entries(accentsMap)) {
            const regex = new RegExp(accented, 'g');
            text = text.replace(regex, plain);
            text = text.replace(regex.source.toUpperCase(), plain.toUpperCase());
        }

        return text;
    }

    private normalizeVector(vector: number[]): number[] {
        const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
        return magnitude > 0 ? vector.map(val => val / magnitude) : vector;
    }

    private async listAvailableModels(): Promise<{ models: string[]; recommended: string }> {
        try {
            const response = await fetch(`${this.ollamaBaseUrl}/api/tags`);
            if (!response.ok) {
                throw new Error(`Failed to fetch models: ${response.statusText}`);
            }

            const data = await response.json();
            const models = data.models?.map((m: any) => m.name) || [];

            return {
                models,
                recommended: 'nomic-embed-text'
            };
        } catch (error) {
            return {
                models: ['nomic-embed-text'],
                recommended: 'nomic-embed-text'
            };
        }
    }

    private async testSimilarity(
        text1: string,
        text2: string,
        model: string = 'nomic-embed-text'
    ): Promise<{ similarity: number; text1: string; text2: string; model: string }> {
        const [emb1, emb2] = await Promise.all([
            this.generateEmbedding(text1, model),
            this.generateEmbedding(text2, model)
        ]);

        const similarity = this.cosineSimilarity(emb1.embedding, emb2.embedding);

        return {
            similarity,
            text1,
            text2,
            model
        };
    }

    private cosineSimilarity(a: number[], b: number[]): number {
        if (a.length !== b.length) {
            throw new Error('Vectors must have the same length');
        }

        let dotProduct = 0;
        let normA = 0;
        let normB = 0;

        for (let i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
    }
}
