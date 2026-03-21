// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import rehypeMermaid from 'rehype-mermaid';

// https://astro.build/config
export default defineConfig({
	site: 'https://dweng0.github.io',
	base: '/POPPINS',
	markdown: {
		rehypePlugins: [[rehypeMermaid, { strategy: 'img-svg' }]],
	},
	integrations: [
		starlight({
			title: 'poppins',
			logo: {
				src: './src/assets/cute_sheep.svg',
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/dweng0/POPPINS' },
			],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: 'getting-started/introduction' },
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Quick Start', slug: 'getting-started/quick-start' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Writing BDD Scenarios', slug: 'guides/writing-scenarios' },
						{ label: 'The Evolution Loop', slug: 'guides/evolution-loop' },
						{ label: 'Using Claude Code', slug: 'guides/claude-code' },
						{ label: 'GitHub Issues', slug: 'guides/github-issues' },
					],
				},
				{
					label: 'Architecture',
					items: [
						{ label: 'How It Works', slug: 'architecture/how-it-works' },
						{ label: 'Agent Internals', slug: 'architecture/agent-internals' },
						{ label: 'File Reference', slug: 'architecture/file-reference' },
					],
				},
			],
		}),
	],
});
