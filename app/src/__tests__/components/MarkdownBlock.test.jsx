import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import MarkdownBlock, { MarkdownBlocks } from '../../components/learning/MarkdownBlock';
import { buildContentSections, parseMarkdownBlocks } from '../../components/learning/markdownParser';

describe('parseMarkdownBlocks', () => {
  it('keeps blank lines inside fenced code and records the language', () => {
    const blocks = parseMarkdownBlocks([
      'Consider this:',
      '',
      '```python',
      'class Config:',
      '    _instance = None',
      '',
      '',
      '    def __new__(cls):',
      '        return cls._instance',
      '```',
      '',
      'What happens?'
    ].join('\n'));

    expect(blocks.map((block) => block.type)).toEqual(['paragraph', 'code', 'paragraph']);
    expect(blocks[1].language).toBe('python');
    expect(blocks[1].text).toBe('class Config:\n    _instance = None\n\n\n    def __new__(cls):\n        return cls._instance');
  });

  it('parses a pipe table with header, alignment and escaped pipes', () => {
    const [table] = parseMarkdownBlocks([
      '| Pattern | Use when | Cost |',
      '|:--------|:--------:|-----:|',
      '| Singleton | one instance `a \\| b` | low |',
      '| Factory | creation varies | medium |'
    ].join('\n'));

    expect(table.type).toBe('table');
    expect(table.header).toEqual(['Pattern', 'Use when', 'Cost']);
    expect(table.align).toEqual(['left', 'center', 'right']);
    expect(table.rows).toHaveLength(2);
    expect(table.rows[0][1]).toBe('one instance `a | b`');
  });

  it('turns a bold-labelled blockquote into a callout', () => {
    const [callout] = parseMarkdownBlocks('> **Interview tip:** Say *why* first.\n> Then show code.');
    expect(callout).toMatchObject({ type: 'callout', label: 'Interview tip', tone: 'tip' });
    expect(callout.blocks[0]).toEqual({ type: 'paragraph', text: 'Say *why* first. Then show code.' });
  });

  it('reads fence attributes and diagram placeholders', () => {
    const blocks = parseMarkdownBlocks([
      '```pseudo title="hello_agent.py (trimmed)"',
      'CREATE agent = Agent that uses model',
      '```',
      '',
      '```bash reveal title="terminal"',
      'aws configure',
      '```',
      '',
      '{{diagram:2}}'
    ].join('\n'));

    expect(blocks[0]).toMatchObject({ type: 'code', language: 'pseudo', title: 'hello_agent.py (trimmed)', reveal: false });
    expect(blocks[1]).toMatchObject({ type: 'code', language: 'bash', title: 'terminal', reveal: true, text: 'aws configure' });
    expect(blocks[2]).toEqual({ type: 'diagram', index: 2 });
  });
});

describe('buildContentSections', () => {
  it('keeps section ids and ignores ## headings inside fences', () => {
    const sections = buildContentSections([
      '# Singleton',
      'Intro text.',
      '## Concepts Covered',
      '- one',
      '```markdown',
      '## not a section',
      '',
      '```',
      '## Practice Loop',
      'Do the work.'
    ].join('\n'));

    expect(sections.map((section) => section.id)).toEqual(['introduction', 'concepts-covered', 'practice-loop']);
    expect(sections[1].blocks[1]).toMatchObject({ type: 'code', text: '## not a section\n' });
  });
});

describe('MarkdownBlock', () => {
  it('renders fenced code with a language label and blank lines preserved', () => {
    const { container } = render(
      <MarkdownBlock text={'```python\nx = 1\n\ny = 2\n```'} />
    );

    expect(screen.getByText('python')).toHaveClass('md-code__label');
    const code = container.querySelector('pre.chapter-code-block code.language-python');
    expect(code.textContent).toBe('x = 1\n\ny = 2');
  });

  it('renders a table with a header row', () => {
    render(<MarkdownBlock text={'| Name | Value |\n|---|---|\n| `a` | **1** |'} />);

    const table = screen.getByRole('table');
    expect(within(table).getAllByRole('columnheader').map((cell) => cell.textContent)).toEqual(['Name', 'Value']);
    const cells = within(table).getAllByRole('cell');
    expect(cells[0].querySelector('code')).toHaveTextContent('a');
    expect(cells[1].querySelector('strong')).toHaveTextContent('1');
  });

  it('renders callouts with a styled label', () => {
    render(<MarkdownBlock text={'> **Pitfall:** Mutable default arguments are shared.'} />);

    const note = screen.getByRole('note');
    expect(note).toHaveClass('md-callout', 'md-callout--caution');
    expect(within(note).getByText('Pitfall')).toHaveClass('md-callout__label');
    expect(note).toHaveTextContent('Mutable default arguments are shared.');
  });

  it('renders inline links in a new tab and drops unsafe hrefs', () => {
    render(<MarkdownBlock text={'Read [PEP 8](https://peps.python.org/pep-0008/) and [this](javascript:alert(1)).'} />);

    const link = screen.getByRole('link', { name: 'PEP 8' });
    expect(link).toHaveAttribute('href', 'https://peps.python.org/pep-0008/');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noreferrer');
    expect(screen.queryByRole('link', { name: 'this' })).not.toBeInTheDocument();
  });

  it('renders pseudo code with highlighted keywords and comments', () => {
    const { container } = render(<MarkdownBlock text={'```pseudo title="agent"\nSET region = "us-east-1"   // default\n```'} />);

    expect(screen.getByText('Pseudo code · agent')).toHaveClass('md-code__label');
    expect(container.querySelector('.md-pseudo__kw')).toHaveTextContent('SET');
    expect(container.querySelector('.md-pseudo__comment')).toHaveTextContent('// default');
  });

  it('hides revealable code behind a View code toggle with a copy button', () => {
    const { container } = render(<MarkdownBlock text={'```bash reveal title="terminal"\naws configure\n```'} />);

    const details = container.querySelector('details.md-reveal');
    expect(details).not.toHaveAttribute('open');
    expect(within(details).getByText('View code')).toBeInTheDocument();
    expect(within(details).getByRole('button', { name: 'Copy' })).toBeInTheDocument();
    expect(details.querySelector('code.language-bash')).toHaveTextContent('aws configure');
  });

  it('places a diagram inline by its order index', () => {
    const diagrams = new Map([[1, { orderIndex: 1, title: 'Agent loop', svgContent: '<svg viewBox="0 0 10 10"><text>loop</text></svg>' }]]);
    const { container } = render(<MarkdownBlocks blocks={parseMarkdownBlocks('Before\n\n{{diagram:1}}\n\nAfter')} diagrams={diagrams} />);

    expect(screen.getByRole('img', { name: 'Agent loop' })).toBeInTheDocument();
    expect(container.querySelector('.md-diagram svg')).toHaveTextContent('loop');
  });

  it('does not treat snake_case identifiers as italics', () => {
    const { container } = render(<MarkdownBlock text="Call get_user_by_id and *then* cache it." />);
    expect(container.querySelectorAll('em')).toHaveLength(1);
    expect(container).toHaveTextContent('Call get_user_by_id and then cache it.');
  });
});
