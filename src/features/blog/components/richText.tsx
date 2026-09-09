type RichTextBlock = {
  type?: string;
  text?: string;
  level?: number;
  items?: string[];
  url?: string;
  alt?: string;
};

export default function RichText({ blocks }: { blocks: unknown[] }) {
  return (
    <div className="prose prose-slate max-w-none dark:prose-invert">
      {blocks.map((rawBlock, index) => {
        const block = rawBlock as RichTextBlock;
        const key = `${block.type ?? "block"}-${index}`;
        if (block.type === "heading") {
          const Heading = block.level === 3 ? "h3" : "h2";
          return <Heading key={key}>{block.text}</Heading>;
        }
        if (block.type === "list") {
          return (
            <ul key={key}>
              {(block.items ?? []).map((item) => <li key={item}>{item}</li>)}
            </ul>
          );
        }
        if (block.type === "quote") {
          return <blockquote key={key}>{block.text}</blockquote>;
        }
        if (block.type === "image" && block.url) {
          return (
            <figure key={key}>
              <img src={block.url} alt={block.alt ?? ""} className="rounded-lg" />
              {block.text && <figcaption>{block.text}</figcaption>}
            </figure>
          );
        }
        if (block.type === "link" && block.url) {
          return <p key={key}><a href={block.url}>{block.text ?? block.url}</a></p>;
        }
        return <p key={key}>{block.text}</p>;
      })}
    </div>
  );
}
