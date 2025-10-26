"""
Association Generator Service
Creates memorable associations between room objects and concepts using Groq LLM
"""

import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
import json
from logging_config import setup_logger

# Load environment variables
load_dotenv()

# Set up logger
logger = setup_logger(__name__, "association_generation.log")


class AssociationGenerator:
    """Service for generating mnemonic associations using Groq LLM."""
    
    def __init__(self):
        """Initialize Association Generator with Groq client."""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            error_msg = "GROQ_API_KEY not found in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.groq_client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"  # Fast, powerful model
        logger.info(f"AssociationGenerator initialized with model: {self.model_name}")
    
    def generate_associations(
        self, 
        concepts: List[Dict[str, str]], 
        room_objects: List[Dict[str, str]],
        pdf_text: str = None
    ) -> List[Dict]:
        """
        Generate memorable associations between concepts and room objects.
        
        Args:
            concepts: List of concepts with 'concept' and 'description'
            room_objects: List of room objects with 'object_name' and 'short_description'
            pdf_text: Optional PDF text for additional context
            
        Returns:
            List of associations with concept, object, and memorable association text
        """
        logger.info(f"Starting association generation for {len(concepts)} concepts and {len(room_objects)} objects")
        
        if not concepts or not room_objects:
            error_msg = "Concepts and room objects are required"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # If more concepts than objects, limit concepts to available objects
        if len(concepts) > len(room_objects):
            logger.warning(f"More concepts ({len(concepts)}) than objects ({len(room_objects)}). Using only first {len(room_objects)} concepts.")
            concepts = concepts[:len(room_objects)]
            logger.info(f"Limited to {len(concepts)} concepts to match available objects")
        
        logger.debug(f"Concepts: {json.dumps(concepts[:2], indent=2)}...")  # Log first 2 for debugging
        logger.debug(f"Room objects: {json.dumps(room_objects[:2], indent=2)}...")
        
        system_prompt = """Sen Hafıza Sarayı (Method of Loci) tekniği için akılda kalıcı ilişkilendirmeler oluşturmada uzmansın.

ÖNEMLİ: Tüm yanıtların TÜRKÇE olmalıdır. İngilizce kelime veya cümle kullanma.

Görevin, oda nesneleri ile çalışma kavramları arasında canlı, akılda kalıcı ve genellikle eğlenceli ilişkilendirmeler oluşturmak.

Etkili ilişkilendirmeler için kurallar:
1. CANLI ve GÖRSEL olmalı - birden fazla duyuyu harekete geçir
2. Uygun olduğunda abartı, absürtlük veya mizah kullan
3. Fiziksel nesneyi kavramın anlamıyla bağla
4. İlişkilendirmeleri MUTLAKA 4-6 CÜMLE olarak yaz - detaylı ve akılda kalıcı
5. Kişisel ve duygusal olarak ilgi çekici yap
6. Mümkün olduğunda hareket ve eylem kullan
7. HER ŞEY TÜRKÇE OLMALI - hiç İngilizce kullanma

Örnek uzunluk (4-6 cümle):
"Lambayı gördüğünde, onun parlak ışığının nasıl güneş ışığı gibi odayı aydınlattığını fark et. Bu parlak sarı ışık, bitkilerin fotosentez yapmasını sağlayan güneş ışığını temsil ediyor. Lambanın içindeki flaman, sanki bir yapraktaki klorofil gibi ışığı enerjiye dönüştürüyor. Her ışık huzmesi, bir bitki hücresinin içinde gerçekleşen mucizevi dönüşümü simgeliyor. Bu lambaya her baktığında, fotosentezin ışığı hayata dönüştüren büyülü sürecini hatırlayacaksın."

Çıktı formatı (TAMAMEN TÜRKÇE):
{
  "associations": [
    {
      "concept": "Kavram adı (Türkçe)",
      "concept_description": "Kavram açıklaması (Türkçe)",
      "object_name": "Nesne adı (Türkçe)",
      "object_description": "Nesne açıklaması (Türkçe)",
      "association": "4-6 cümlelik akılda kalıcı ilişkilendirme metni (TAMAMEN TÜRKÇE)"
    }
  ]
}"""

        # Prepare concepts and objects for the prompt
        concepts_text = json.dumps([{
            "concept": c.get("concept", ""),
            "description": c.get("description", "")
        } for c in concepts], indent=2)
        
        objects_text = json.dumps([{
            "object_name": o.get("object_name", ""),
            "description": o.get("short_description", o.get("object_description", ""))
        } for o in room_objects], indent=2)
        
        user_prompt = f"""Bu kavramlar ile oda nesneleri arasında TÜRKÇE akılda kalıcı ilişkilendirmeler oluştur.

ÇOK ÖNEMLİ: 
- Tüm yanıtların TÜRKÇE olması zorunludur
- Her ilişkilendirme MUTLAKA 4-6 cümle olmalıdır
- İngilizce kelime kullanma

Öğrenilecek kavramlar:
{concepts_text}

Mevcut oda nesneleri:
{objects_text}

Talimatlar:
1. Her kavramı BİR benzersiz oda nesnesiyle eşleştir
2. Her eşleştirme için canlı, akılda kalıcı bir ilişkilendirme oluştur
3. İlişkilendirmeleri MUTLAKA 4-6 CÜMLE olarak yaz
4. İlişkilendirmeleri görsel, duygusal ve ilgi çekici yap
5. Detaylı anlatım yap - açıklayıcı ol
6. TAMAMEN TÜRKÇE yaz - tüm açıklamalar ve ilişkilendirmeler Türkçe olmalı
7. Sadece belirtilen formatta geçerli JSON döndür

Örnek uzun ilişkilendirme (4-6 cümle):
"Bilgisayar monitörünü izlerken, ekranın nasıl parlak renklerle dolup taştığını hayal et. Bu renkli pikseller, bilginin dijital dünyada nasıl kodlandığını gösteriyor. Her piksel, veri bitlerinin görsel bir temsili gibi, kavramın temel yapı taşlarını simgeliyor. Monitörün içindeki elektronlar, sanki kavramın farklı yönleri gibi hızla hareket ediyor ve bilgiyi oluşturuyor. Ekrana her dokunduğunda, parmaklarının altında bu bilgi akışını hissediyorsun. Bu görsel deneyim, kavramı zihninde kristalize ediyor ve unutulmaz kılıyor."

UNUTMA: Her ilişkilendirme bu örnekteki gibi DETAYLI olmalı!"""

        # Add PDF context if available (truncated)
        if pdf_text:
            max_context = 2000
            if len(pdf_text) > max_context:
                pdf_text = pdf_text[:max_context] + "..."
            user_prompt += f"\n\nAdditional context from study material:\n{pdf_text}"
            logger.debug(f"Added PDF context ({len(pdf_text)} chars)")

        try:
            logger.info(f"Calling Groq API with model: {self.model_name}")
            logger.debug(f"System prompt length: {len(system_prompt)} chars")
            logger.debug(f"User prompt length: {len(user_prompt)} chars")
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Higher temperature for more creative associations
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            # Log API response metadata
            logger.info(f"API call successful. Tokens used: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}")
            
            # Parse response
            result_text = response.choices[0].message.content
            logger.debug(f"Raw API response ({len(result_text)} chars): {result_text[:200]}...")
            
            result = json.loads(result_text)
            logger.info("Successfully parsed JSON response")
            
            # Validate and format
            if "associations" in result and isinstance(result["associations"], list):
                associations = result["associations"]
                logger.info(f"Found {len(associations)} associations in response")
                
                # Ensure each association has required fields
                formatted_associations = []
                for i, assoc in enumerate(associations):
                    if all(key in assoc for key in ["concept", "object_name", "association"]):
                        formatted_associations.append({
                            "concept": assoc["concept"],
                            "concept_description": assoc.get("concept_description", ""),
                            "object_name": assoc["object_name"],
                            "object_description": assoc.get("object_description", ""),
                            "association": assoc["association"]
                        })
                        logger.debug(f"Association {i+1}: {assoc['concept']} -> {assoc['object_name']}")
                    else:
                        logger.warning(f"Skipping invalid association {i+1}: missing required fields")
                
                logger.info(f"Successfully generated {len(formatted_associations)} valid associations")
                return formatted_associations
            else:
                error_msg = "Invalid response format from LLM - missing 'associations' array"
                logger.error(f"{error_msg}. Response structure: {list(result.keys())}")
                return {"error": error_msg}
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error(f"Raw response that failed to parse: {result_text[:500]}...")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error generating associations: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}

    def generate_story_associations(
        self, 
        concepts: List[Dict[str, str]], 
        room_objects: List[Dict[str, str]],
        pdf_text: str = None
    ) -> List[Dict]:
        """
        Generate memorable associations with story transitions between consecutive rows.
        
        Each association will:
        1. Describe the vivid link between the object and concept
        2. Add a smooth story transition to the next object/concept
        
        This creates a flowing narrative that helps users remember the sequence.
        
        Args:
            concepts: List of concepts with 'concept' and 'description'
            room_objects: List of room objects with 'object_name' and 'short_description'
            pdf_text: Optional PDF text for additional context
            
        Returns:
            List of associations with concept, object, and story-based association text
        """
        logger.info(f"Starting STORY-BASED association generation for {len(concepts)} concepts and {len(room_objects)} objects")
        
        if not concepts or not room_objects:
            error_msg = "Concepts and room objects are required"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # If more concepts than objects, limit concepts to available objects
        if len(concepts) > len(room_objects):
            logger.warning(f"More concepts ({len(concepts)}) than objects ({len(room_objects)}). Using only first {len(room_objects)} concepts.")
            concepts = concepts[:len(room_objects)]
            logger.info(f"Limited to {len(concepts)} concepts to match available objects")
        
        logger.debug(f"Concepts: {json.dumps(concepts[:2], indent=2)}...")
        logger.debug(f"Room objects: {json.dumps(room_objects[:2], indent=2)}...")
        
        system_prompt = """Sen Hafıza Sarayı (Method of Loci) tekniği için hikaye tabanlı akılda kalıcı ilişkilendirmeler oluşturmada uzmansın.

Görevin, her ilişkilendirmenin doğal bir şekilde bir sonrakine aktığı BİRBİRİNE BAĞLI BİR HİKAYE oluşturmak.

Her nesne-kavram çifti için:
1. Canlı, akılda kalıcı bir ilişkilendirme oluştur (4-6 cümle)
2. SONRAKİ nesneye/kavrama götüren KISA bir hikaye geçişi ekle (1-2 cümle)

Bu, kullanıcıların sırayı hatırlamasına yardımcı olan akıcı bir anlatı oluşturur.

Kurallar:
- İlişkilendirmeleri CANLI ve GÖRSEL yap - birden fazla duyuyu harekete geçir
- Uygun olduğunda abartı, absürtlük veya mizah kullan
- Geçiş doğal hissettirmeli, sanki odada yürüyormuşsun gibi
- Geçişler mekansal harekete atıfta bulunabilir ("arkana döndüğünde görürsün...", "yakınında duruyor...")
- Hikayeyi ilgi çekici ve takip edilmesi kolay tut
- SON öğe için geçiş gerekmez (sadece ilişkilendirme ile bitir)
- TAMAMEN TÜRKÇE yaz

Çıktı formatı (TÜRKÇE):
{
  "associations": [
    {
      "concept": "Kavram adı",
      "concept_description": "Kavram açıklaması",
      "object_name": "Nesne adı",
      "object_description": "Nesne açıklaması",
      "association": "4-6 cümlelik akılda kalıcı ilişkilendirme, ardından bir sonraki nesneye/kavrama yumuşak bir geçiş"
    }
  ]
}"""

        # Prepare concepts and objects with SEQUENCE information
        concepts_text = json.dumps([{
            "position": i + 1,
            "concept": c.get("concept", ""),
            "description": c.get("description", "")
        } for i, c in enumerate(concepts)], indent=2)
        
        objects_text = json.dumps([{
            "position": i + 1,
            "object_name": o.get("object_name", ""),
            "description": o.get("short_description", o.get("object_description", ""))
        } for i, o in enumerate(room_objects)], indent=2)
        
        user_prompt = f"""Bu kavramlar ile oda nesneleri arasında TÜRKÇE HİKAYE TABANLI bir dizi akılda kalıcı ilişkilendirme oluştur.

ÇOK ÖNEMLİ: 
- Tüm yanıtların TÜRKÇE olması zorunludur
- Her ilişkilendirme MUTLAKA 4-6 cümle + geçiş (1-2 cümle) olmalıdır
- İngilizce kelime kullanma
- İlişkilendirmeler akıcı bir hikaye oluşturmalı
- Her ilişkilendirme (son hariç) bir sonraki nesneye kısa bir geçişle bitmelidir

Sırayla öğrenilecek kavramlar:
{concepts_text}

Sırayla mevcut oda nesneleri:
{objects_text}

Talimatlar:
1. Her kavramı karşılık gelen oda nesnesiyle eşleştir (pozisyona göre)
2. 1'den {len(concepts)-1}'e kadar olan öğeler için: 
   - Canlı ilişkilendirme (MUTLAKA 4-6 cümle, TÜRKÇE) 
   - Sonraki nesneye kısa geçiş (1-2 cümle, TÜRKÇE)
3. SON öğe (#{len(concepts)}) için: 
   - Sadece canlı ilişkilendirme (MUTLAKA 4-6 cümle, TÜRKÇE)
   - Geçiş yok
4. Hikayeyi doğal bir şekilde akıt, sanki odada yürüyormuşsun gibi
5. TAMAMEN TÜRKÇE yaz - tüm ilişkilendirmeler ve geçişler Türkçe olmalı
6. Detaylı anlatım yap
7. Sadece belirtilen formatta geçerli JSON döndür

Örnek yapı (öğe 1 için - 4-6 cümle + geçiş):
"association": "Siyah kalemi eline aldığında, mürekkebinin nasıl koyu bir renkte aktığını hisset. Bu koyu siyah renk, kavramın derinliğini ve karmaşıklığını simgeliyor. Kalemin ucundan akan mürekkep, sanki bilginin zihninde akması gibi, kesintisiz ve akıcı bir şekilde kağıda dökülüyor. Her harfi yazarken, kavramın farklı yönlerini kağıda aktarıyorsun. Bu deneyim, kavramı somut ve elle tutulur hale getiriyor, zihninde kalıcı bir iz bırakıyor. Kalemi masaya bırakırken, hemen yanında duran bilgisayar monitörünü fark ediyorsun."

Örnek yapı (SON öğe için - sadece 4-6 cümle, geçiş yok):
"association": "Asker figürünü eline aldığında, onun sağlam duruşunu ve kararlılığını hissediyorsun. Bu figürün her detayı, kavramın güçlü ve dayanıklı yapısını temsil ediyor. Askerin üzerindeki her parça ekipman, kavramın farklı bileşenlerini simgeliyor. Figürü döndürdükçe, kavramın çok yönlü doğasını farklı açılardan görüyorsun. Bu küçük figür, zihninde büyük bir kavramı temsil ediyor ve bu görsel imge her zaman seninle kalacak."

UNUTMA: Her ilişkilendirme bu örneklerdeki gibi DETAYLI olmalı!"""

        # Add PDF context if available (truncated)
        if pdf_text:
            max_context = 1500
            if len(pdf_text) > max_context:
                pdf_text = pdf_text[:max_context] + "..."
            user_prompt += f"\n\nContext from study material:\n{pdf_text}"
            logger.debug(f"Added PDF context ({len(pdf_text)} chars)")

        try:
            logger.info(f"Calling Groq API for story-based associations with model: {self.model_name}")
            logger.debug(f"System prompt length: {len(system_prompt)} chars")
            logger.debug(f"User prompt length: {len(user_prompt)} chars")
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.85,  # Slightly higher for creative story flow
                max_tokens=4000,   # More tokens for story transitions
                response_format={"type": "json_object"}
            )
            
            # Log API response metadata
            logger.info(f"API call successful. Tokens used: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}")
            
            # Parse response
            result_text = response.choices[0].message.content
            logger.debug(f"Raw API response ({len(result_text)} chars): {result_text[:200]}...")
            
            result = json.loads(result_text)
            logger.info("Successfully parsed JSON response")
            
            # Validate and format
            if "associations" in result and isinstance(result["associations"], list):
                associations = result["associations"]
                logger.info(f"Found {len(associations)} story-based associations in response")
                
                # Ensure each association has required fields
                formatted_associations = []
                for i, assoc in enumerate(associations):
                    if all(key in assoc for key in ["concept", "object_name", "association"]):
                        formatted_associations.append({
                            "concept": assoc["concept"],
                            "concept_description": assoc.get("concept_description", ""),
                            "object_name": assoc["object_name"],
                            "object_description": assoc.get("object_description", ""),
                            "association": assoc["association"]
                        })
                        logger.debug(f"Story association {i+1}: {assoc['concept']} -> {assoc['object_name']}")
                        logger.debug(f"  Length: {len(assoc['association'])} chars")
                    else:
                        logger.warning(f"Skipping invalid association {i+1}: missing required fields")
                
                logger.info(f"Successfully generated {len(formatted_associations)} valid story-based associations")
                return formatted_associations
            else:
                error_msg = "Invalid response format from LLM - missing 'associations' array"
                logger.error(f"{error_msg}. Response structure: {list(result.keys())}")
                return {"error": error_msg}
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error(f"Raw response that failed to parse: {result_text[:500]}...")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error generating story-based associations: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python association_generator.py <concepts_json> <objects_json> [pdf_text_file]")
        print("\nExample:")
        print("  python association_generator.py concepts.json room_objects.json study_material.txt")
        sys.exit(1)
    
    concepts_file = sys.argv[1]
    objects_file = sys.argv[2]
    text_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Load concepts
    if not os.path.exists(concepts_file):
        print(f"Error: Concepts file not found: {concepts_file}")
        sys.exit(1)
    
    with open(concepts_file, 'r', encoding='utf-8') as f:
        concepts = json.load(f)
    
    # Load room objects
    if not os.path.exists(objects_file):
        print(f"Error: Objects file not found: {objects_file}")
        sys.exit(1)
    
    with open(objects_file, 'r', encoding='utf-8') as f:
        room_objects = json.load(f)
    
    # Load PDF text if provided
    pdf_text = None
    if text_file and os.path.exists(text_file):
        with open(text_file, 'r', encoding='utf-8') as f:
            pdf_text = f.read()
    
    print(f"Generating associations for {len(concepts)} concepts and {len(room_objects)} objects...")
    
    generator = AssociationGenerator()
    associations = generator.generate_associations(concepts, room_objects, pdf_text)
    
    if isinstance(associations, dict) and "error" in associations:
        print(f"Error: {associations['error']}")
    else:
        print(f"\nGenerated {len(associations)} associations:\n")
        for i, assoc in enumerate(associations, 1):
            print(f"{i}. {assoc['concept']} → {assoc['object_name']}")
            print(f"   {assoc['association']}\n")
