const messages = [
  { from: "user", text: "Show my wardrobe" },
  {
    from: "bot",
    text: "🌸 Your Wardrobe — 12 fragrances\n\n♡ Chanel Coco Mademoiselle\n♡ Diptyque Do Son\n♡ Byredo Gypsy Water\n♡ Le Labo Santal 33",
  },
  { from: "user", text: "I feel romantic today" },
  {
    from: "bot",
    text: "💕 Perfect for a romantic mood:\n\nChanel Coco Mademoiselle\nWarm · Floral · Sensual\n\nEstimated longevity: 8h+",
  },
];

const PhoneMockup = () => (
  <div className="relative w-[280px] sm:w-[300px]">
    {/* Phone frame */}
    <div className="rounded-[2.5rem] bg-foreground/5 p-3 soft-shadow-lg">
      <div className="rounded-[2rem] bg-card overflow-hidden">
        {/* Status bar */}
        <div className="flex items-center justify-between px-6 pt-3 pb-2">
          <span className="text-[10px] text-muted-foreground font-medium">9:41</span>
          <div className="flex gap-1">
            <div className="w-3.5 h-1.5 rounded-sm bg-muted-foreground/30" />
            <div className="w-1.5 h-1.5 rounded-sm bg-muted-foreground/30" />
          </div>
        </div>

        {/* Chat header */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs">🌺</div>
          <div>
            <p className="text-sm font-semibold text-foreground">50 scent</p>
            <p className="text-[10px] text-muted-foreground">online</p>
          </div>
        </div>

        {/* Messages */}
        <div className="p-3 space-y-2.5 min-h-[320px]">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-[85%] ${
                msg.from === "user" ? "ml-auto" : "mr-auto"
              }`}
            >
              <div
                className={`rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                  msg.from === "user"
                    ? "bg-primary text-primary-foreground rounded-br-md"
                    : "bg-secondary text-secondary-foreground rounded-bl-md"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Input bar */}
        <div className="flex items-center gap-2 px-3 py-2.5 border-t border-border">
          <div className="flex-1 h-8 rounded-full bg-muted px-3 flex items-center">
            <span className="text-[11px] text-muted-foreground">Message...</span>
          </div>
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm">↑</div>
        </div>
      </div>
    </div>
  </div>
);

export default PhoneMockup;
