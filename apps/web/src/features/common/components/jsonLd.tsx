export type JsonLdNode = Record<string, unknown>;

// `<` is escaped so untrusted strings can never close the script tag.
function serialize(data: unknown) {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

export default function JsonLd({ nodes }: { nodes: JsonLdNode[] }) {
  if (nodes.length === 0) return null;
  const data = { "@context": "https://schema.org", "@graph": nodes };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: serialize(data) }}
    />
  );
}
