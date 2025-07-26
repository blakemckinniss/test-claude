import React, { useEffect, useRef } from 'react';
import { TextDisplay } from '../../types/game.types';
import { Card, CardContent } from './card';
import { ScrollArea } from './scroll-area';
import { TextAnimate } from '../magicui/text-animate';

interface StoryTextAreaProps {
  texts: TextDisplay[];
}

const StoryTextArea: React.FC<StoryTextAreaProps> = ({ texts }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [texts]);

  const renderText = (textObj: TextDisplay, index: number) => {
    const { text, type, speaker } = textObj;

    let textClass = 'mb-4 leading-relaxed';
    
    switch (type) {
      case 'dialogue':
        textClass += ' italic text-blue-800 font-medium';
        break;
      case 'action':
        textClass += ' text-green-800 font-semibold';
        break;
      case 'damage':
        textClass += ' text-red-800 font-bold';
        break;
      case 'heal':
        textClass += ' text-green-700 font-bold';
        break;
      default:
        textClass += ' text-ink-black';
    }

    return (
      <div key={index} className={textClass}>
        {speaker && (
          <strong className="text-amber-800 block mb-1 font-medieval">{speaker}:</strong>
        )}
        {index === 0 && type === 'narration' && (
          <span className="float-left text-6xl leading-none pr-2 text-amber-800 font-medieval drop-shadow-lg">
            {text.charAt(0)}
          </span>
        )}
        {type === 'narration' && index === texts.length - 1 ? (
          <TextAnimate
            animation="fadeIn"
            by="word"
            delay={0.1}
            duration={1.2}
            className={`${index === 0 ? 'text-sm' : ''} inline`}
          >
            {index === 0 ? text.slice(1) : text}
          </TextAnimate>
        ) : (
          <span className={index === 0 && type === 'narration' ? 'text-sm' : ''}>
            {index === 0 && type === 'narration' ? text.slice(1) : text}
          </span>
        )}
      </div>
    );
  };

  return (
    <Card 
      className="story-text-area bg-gradient-to-br from-parchment-light/98 to-parchment/95 border-2 border-parchment-shadow/50 relative shadow-lg"
      style={{
        backgroundImage: `
          linear-gradient(45deg, transparent 10px, rgba(139, 69, 19, 0.08) 10px, rgba(139, 69, 19, 0.08) 11px, transparent 11px),
          linear-gradient(-45deg, transparent 10px, rgba(139, 69, 19, 0.08) 10px, rgba(139, 69, 19, 0.08) 11px, transparent 11px)
        `
      }}
    >
      <CardContent className="p-6">
        <ScrollArea className="max-h-96" ref={containerRef}>
          {texts.length === 0 ? (
            <div className="text-center text-ink-black/60 py-8">
              <TextAnimate animation="blurIn" by="word" className="font-medieval text-lg">
                Your adventure begins...
              </TextAnimate>
            </div>
          ) : (
            texts.map(renderText)
          )}
        </ScrollArea>
        
        {/* Decorative corners */}
        <div className="absolute top-2 left-2 w-4 h-4 border-l-2 border-t-2 border-amber-800/70" />
        <div className="absolute top-2 right-2 w-4 h-4 border-r-2 border-t-2 border-amber-800/70" />
        <div className="absolute bottom-2 left-2 w-4 h-4 border-l-2 border-b-2 border-amber-800/70" />
        <div className="absolute bottom-2 right-2 w-4 h-4 border-r-2 border-b-2 border-amber-800/70" />
      </CardContent>
    </Card>
  );
};

export default StoryTextArea;