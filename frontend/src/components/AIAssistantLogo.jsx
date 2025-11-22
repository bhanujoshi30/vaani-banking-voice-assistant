import PropTypes from "prop-types";
import "./AIAssistantLogo.css";

/**
 * AI Assistant Logo Component
 * Displays the Sun National Bank AI Assistant logo
 * - Central orange speech bubble with "AI" text
 * - Outer radiating sun pattern with 8 prominent teardrop elements
 * - Animated with continuous motion for enhanced appeal
 */
const AIAssistantLogo = ({ size = 32, showText = false, showAssistant = false, className = "", animated = true }) => {
  const viewBoxSize = 100;
  const padding = 8; // Padding to prevent cropping of sun rays
  const centerX = viewBoxSize / 2;
  const centerY = viewBoxSize / 2;
  const speechBubbleRadius = 18;
  const outerRadius = 45;
  const uniqueId = `logo-${size}-${showText ? 'text' : 'icon'}-${showAssistant ? 'assistant' : ''}`;
  const svgHeight = showAssistant ? viewBoxSize + 20 : viewBoxSize;
  // Adjust viewBox to include padding, and adjust center coordinates accordingly
  const viewBoxWidth = viewBoxSize + (padding * 2);
  const viewBoxHeight = svgHeight + (padding * 2);
  const adjustedCenterX = centerX + padding;
  const adjustedCenterY = centerY + padding;
  
  const animationClass = animated ? "ai-assistant-logo-animated" : "";
  
  return (
    <div className={animationClass}>
      <svg
        width={size}
        height={showAssistant ? size * 1.2 : size}
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        xmlns="http://www.w3.org/2000/svg"
        className={className}
        aria-label="Sun National Bank AI Assistant"
      >
      <defs>
        {/* Orange/golden-orange gradient */}
        <linearGradient id={`orangeGradient-${uniqueId}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FF8C00" stopOpacity="1" />
          <stop offset="50%" stopColor="#FFA500" stopOpacity="1" />
          <stop offset="100%" stopColor="#FFD700" stopOpacity="1" />
        </linearGradient>
      </defs>
      
      {/* All elements centered together - speech bubble stays stationary, rays and teardrops rotate */}
      <g transform={`translate(${adjustedCenterX}, ${adjustedCenterY})`}>
        {/* Rotating elements - rays and teardrops */}
        <g className="sun-rays">
          {animated && (
            <animateTransform
              attributeName="transform"
              type="rotate"
              values="0;360"
              dur="20s"
              repeatCount="indefinite"
            />
          )}
          {/* Thin rays */}
          {[...Array(24)].map((_, i) => {
            const angle = (i * 360) / 24;
            const rad = (angle * Math.PI) / 180;
            const innerRadius = speechBubbleRadius + 5;
            const outerRadiusRay = outerRadius - 3;
            const x1 = Math.cos(rad) * innerRadius;
            const y1 = Math.sin(rad) * innerRadius;
            const x2 = Math.cos(rad) * outerRadiusRay;
            const y2 = Math.sin(rad) * outerRadiusRay;
            return (
              <line
                key={`ray-${i}`}
                className="sun-ray"
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={`url(#orangeGradient-${uniqueId})`}
                strokeWidth="1.5"
                strokeLinecap="round"
                fill="none"
              />
            );
          })}
          
          {/* 8 prominent teardrop-shaped elements at cardinal and diagonal positions */}
          {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => {
            const rad = (angle * Math.PI) / 180;
            const distance = outerRadius - 2;
            const x = Math.cos(rad) * distance;
            const y = Math.sin(rad) * distance;
            // Teardrop rotation: angle + 90 to point outward
            const teardropRotation = angle + 90;
            return (
              <g key={`teardrop-group-${i}`} transform={`translate(${x}, ${y}) rotate(${teardropRotation})`}>
                <ellipse
                  className={`teardrop-${i}`}
                  cx="0"
                  cy="0"
                  rx="4"
                  ry="8"
                  fill={`url(#orangeGradient-${uniqueId})`}
                />
              </g>
            );
          })}
        </g>
        
        {/* Central speech bubble (circle with tail) - stationary, perfectly centered */}
        <g className="speech-bubble">
        {/* Main circular part */}
        <circle
          cx="0"
          cy="0"
          r={speechBubbleRadius}
          fill={`url(#orangeGradient-${uniqueId})`}
        />
        
        {/* Speech bubble tail pointing downward */}
        <path
          d={`M -4 ${speechBubbleRadius} L 0 ${speechBubbleRadius + 6} L 4 ${speechBubbleRadius} Z`}
          fill={`url(#orangeGradient-${uniqueId})`}
        />
        
        {/* "AI" text inside the bubble */}
        <text
          x="0"
          y="4"
          fontSize="14"
          fontWeight="bold"
          fill="#333333"
          textAnchor="middle"
          fontFamily="Arial, sans-serif"
          letterSpacing="1"
        >
          AI
        </text>
        </g>
      </g>
      
      {/* "Vaani AI assistant" text below the logo (part of the logo) */}
      {showAssistant && (
        <text
          x={adjustedCenterX}
          y={viewBoxSize + padding + 15}
          fontSize="11"
          fontWeight="800"
          fill="#0f1b2a"
          textAnchor="middle"
          fontFamily="Inter, Arial, sans-serif"
          letterSpacing="0.5"
        >
          <tspan
            fontSize="12"
            fontWeight="900"
            letterSpacing="0.8"
            fill="#0f1b2a"
          >
            Vaani
          </tspan>
          <tspan
            fontSize="10"
            fontWeight="700"
            letterSpacing="0.3"
            fill="#0f1b2a"
            opacity="0.85"
          >
            {" "}AI assistant
          </tspan>
        </text>
      )}
      
      {/* Text below (only if showText is true) */}
      {showText && (
        <g transform={`translate(${adjustedCenterX}, ${viewBoxSize + padding + 20})`}>
          <text
            x="0"
            y="0"
            fontSize="14"
            fontWeight="bold"
            fill="#1E3A5F"
            textAnchor="middle"
            fontFamily="Arial, sans-serif"
            letterSpacing="1"
          >
            SUN NATIONAL BANK
          </text>
          <text
            x="0"
            y="18"
            fontSize="12"
            fontWeight="bold"
            textAnchor="middle"
            fontFamily="Arial, sans-serif"
            letterSpacing="0.5"
          >
            <tspan fill="#4A90E2" fontSize="13">AI</tspan>
            <tspan fill="#1E3A5F"> ASSISTANT</tspan>
          </text>
        </g>
      )}
      </svg>
    </div>
  );
};

AIAssistantLogo.propTypes = {
  size: PropTypes.number,
  showText: PropTypes.bool,
  showAssistant: PropTypes.bool,
  className: PropTypes.string,
  animated: PropTypes.bool,
};

AIAssistantLogo.defaultProps = {
  size: 32,
  showText: false,
  showAssistant: false,
  className: "",
  animated: true,
};

export default AIAssistantLogo;
