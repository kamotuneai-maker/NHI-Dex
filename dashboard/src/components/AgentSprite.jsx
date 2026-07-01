/* Pokédex-style sprite illustrations, one per agent type. */

const sprites = {
  enterprise: ({ dim }) => (
    <svg width={dim} height={dim} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Body */}
      <rect x="20" y="28" width="40" height="32" rx="4" fill="#1F2D4E" />
      {/* Head */}
      <rect x="26" y="14" width="28" height="22" rx="6" fill="#1F2D4E" />
      {/* Eyes */}
      <rect x="31" y="20" width="7" height="7" rx="2" fill="#B8860B" />
      <rect x="42" y="20" width="7" height="7" rx="2" fill="#B8860B" />
      {/* Shield overlay */}
      <path d="M40 34 L51 39 L51 49 Q51 55 40 59 Q29 55 29 49 L29 39 Z" fill="#B8860B" opacity="0.85" />
      <path d="M40 38 L47 41.5 L47 49 Q47 53 40 55.5 Q33 53 33 49 L33 41.5 Z" fill="#F5F2E8" opacity="0.9" />
      {/* Tie */}
      <path d="M36 28 L40 22 L44 28 L42 36 L40 38 L38 36 Z" fill="#B8860B" />
      {/* Legs */}
      <rect x="27" y="58" width="10" height="10" rx="2" fill="#1F2D4E" />
      <rect x="43" y="58" width="10" height="10" rx="2" fill="#1F2D4E" />
      {/* Arms */}
      <rect x="8" y="30" width="12" height="8" rx="4" fill="#1F2D4E" />
      <rect x="60" y="30" width="12" height="8" rx="4" fill="#1F2D4E" />
    </svg>
  ),

  coding: ({ dim }) => (
    <svg width={dim} height={dim} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Terminal body */}
      <rect x="14" y="20" width="52" height="40" rx="5" fill="#1F2D4E" />
      <rect x="14" y="20" width="52" height="10" rx="5" fill="#2D4070" />
      {/* Traffic lights */}
      <circle cx="24" cy="25" r="3" fill="#DC2626" />
      <circle cx="33" cy="25" r="3" fill="#F59E0B" />
      <circle cx="42" cy="25" r="3" fill="#16A34A" />
      {/* Code text */}
      <text x="18" y="43" fontFamily="monospace" fontSize="8" fill="#B8860B">{"<agent>"}</text>
      <text x="18" y="53" fontFamily="monospace" fontSize="8" fill="#F5F2E8">{"  ∿∿∿"}</text>
      <text x="18" y="63" fontFamily="monospace" fontSize="8" fill="#B8860B">{"</agent>"}</text>
      {/* Head above terminal */}
      <circle cx="40" cy="14" r="7" fill="#1F2D4E" />
      <circle cx="37" cy="13" r="2" fill="#B8860B" />
      <circle cx="43" cy="13" r="2" fill="#B8860B" />
      {/* Antenna */}
      <line x1="40" y1="7" x2="40" y2="3" stroke="#B8860B" strokeWidth="2" />
      <circle cx="40" cy="2" r="2" fill="#B8860B" />
    </svg>
  ),

  'client-facing': ({ dim }) => (
    <svg width={dim} height={dim} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Head */}
      <circle cx="40" cy="28" r="16" fill="#1F2D4E" />
      {/* Eyes */}
      <circle cx="34" cy="26" r="4" fill="#B8860B" />
      <circle cx="46" cy="26" r="4" fill="#B8860B" />
      <circle cx="35" cy="25" r="1.5" fill="#F5F2E8" />
      <circle cx="47" cy="25" r="1.5" fill="#F5F2E8" />
      {/* Smile */}
      <path d="M33 33 Q40 38 47 33" stroke="#F5F2E8" strokeWidth="2" fill="none" strokeLinecap="round" />
      {/* Antenna */}
      <line x1="40" y1="12" x2="40" y2="6" stroke="#B8860B" strokeWidth="2" />
      <circle cx="40" cy="5" r="2.5" fill="#B8860B" />
      {/* Speech bubble */}
      <rect x="48" y="6" width="22" height="14" rx="4" fill="#B8860B" />
      <path d="M50 20 L46 24 L54 20" fill="#B8860B" />
      <circle cx="54" cy="13" r="2" fill="#F5F2E8" />
      <circle cx="60" cy="13" r="2" fill="#F5F2E8" />
      <circle cx="66" cy="13" r="2" fill="#F5F2E8" />
      {/* Body */}
      <rect x="26" y="43" width="28" height="24" rx="6" fill="#1F2D4E" />
      {/* Chest badge */}
      <rect x="33" y="49" width="14" height="10" rx="2" fill="#B8860B" opacity="0.7" />
      {/* Legs */}
      <rect x="28" y="65" width="9" height="9" rx="2" fill="#1F2D4E" />
      <rect x="43" y="65" width="9" height="9" rx="2" fill="#1F2D4E" />
    </svg>
  ),

  infrastructure: ({ dim }) => (
    <svg width={dim} height={dim} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Server racks */}
      <rect x="16" y="14" width="48" height="12" rx="3" fill="#1F2D4E" stroke="#B8860B" strokeWidth="1.5" />
      <circle cx="55" cy="20" r="3" fill="#16A34A" />
      <rect x="22" y="17" width="20" height="6" rx="1" fill="#2D4070" />

      <rect x="16" y="30" width="48" height="12" rx="3" fill="#1F2D4E" stroke="#B8860B" strokeWidth="1.5" />
      <circle cx="55" cy="36" r="3" fill="#16A34A" />
      <rect x="22" y="33" width="20" height="6" rx="1" fill="#2D4070" />

      <rect x="16" y="46" width="48" height="12" rx="3" fill="#1F2D4E" stroke="#B8860B" strokeWidth="1.5" />
      <circle cx="55" cy="52" r="3" fill="#F59E0B" />
      <rect x="22" y="49" width="20" height="6" rx="1" fill="#2D4070" />

      {/* Cloud above */}
      <ellipse cx="40" cy="8" rx="12" ry="5" fill="#2D4070" />
      <ellipse cx="32" cy="9" rx="7" ry="4" fill="#2D4070" />
      <ellipse cx="48" cy="9" rx="7" ry="4" fill="#2D4070" />
      {/* Network lines at bottom */}
      <line x1="40" y1="58" x2="24" y2="70" stroke="#B8860B" strokeWidth="1.5" />
      <line x1="40" y1="58" x2="40" y2="72" stroke="#B8860B" strokeWidth="1.5" />
      <line x1="40" y1="58" x2="56" y2="70" stroke="#B8860B" strokeWidth="1.5" />
      <circle cx="24" cy="71" r="3" fill="#B8860B" />
      <circle cx="40" cy="73" r="3" fill="#B8860B" />
      <circle cx="56" cy="71" r="3" fill="#B8860B" />
    </svg>
  ),

  personal: ({ dim }) => (
    <svg width={dim} height={dim} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Ghost body */}
      <path d="M20 40 Q20 16 40 14 Q60 16 60 40 L60 66 L52 60 L44 66 L36 60 L28 66 L20 60 Z"
        fill="#4A4A4A" opacity="0.85" />
      {/* Eyes — glowing red */}
      <ellipse cx="32" cy="36" rx="6" ry="7" fill="#DC2626" />
      <ellipse cx="48" cy="36" rx="6" ry="7" fill="#DC2626" />
      <circle cx="34" cy="35" r="2" fill="#F5F2E8" />
      <circle cx="50" cy="35" r="2" fill="#F5F2E8" />
      {/* Question mark */}
      <text x="33" y="54" fontFamily="monospace" fontSize="14" fontWeight="bold" fill="#B8860B">?</text>
      {/* Shadow underneath */}
      <ellipse cx="40" cy="74" rx="16" ry="4" fill="#1F2D4E" opacity="0.5" />
    </svg>
  ),

  unknown: ({ dim }) => (
    <svg width={dim} height={dim} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Pokéball split circle */}
      <circle cx="40" cy="40" r="28" fill="#F5F2E8" stroke="#4A4A4A" strokeWidth="2.5" />
      <path d="M12 40 A28 28 0 0 1 68 40 Z" fill="#DC2626" />
      <line x1="12" y1="40" x2="68" y2="40" stroke="#4A4A4A" strokeWidth="3" />
      <circle cx="40" cy="40" r="9" fill="#F5F2E8" stroke="#4A4A4A" strokeWidth="2.5" />
      <circle cx="40" cy="40" r="4" fill="#4A4A4A" />
    </svg>
  ),
};

export function AgentSprite({ type, size = 72, customSrc }) {
  const dim = size;

  if (customSrc) {
    return <img src={customSrc} alt={type} width={dim} height={dim} className="object-contain" />;
  }

  const SpriteComponent = sprites[type] || sprites.unknown;
  return <SpriteComponent dim={dim} />;
}
